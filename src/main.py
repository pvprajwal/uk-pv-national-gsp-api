""" Main FastAPI app """
import logging
import os
from datetime import timedelta

from fastapi import Depends, FastAPI
from sqlalchemy.orm.session import Session

from dummy import create_dummy_national_forecast, create_dummy_gsp_forecast
from nowcasting_forecast.database.models import Forecast, ManyForecasts
from database import get_forecasts_for_a_specific_gsp_from_database, get_forecasts_from_database

from nowcasting_forecast.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

version = "0.1.5"
description = """
The Nowcasting API is still under development. It only returns zeros for now.
"""
app = FastAPI(
    title="Nowcasting API",
    version=version,
    description=description,
    contact={
        "name": "Open Climate Fix",
        "url": "https://openclimatefix.org",
        "email": "info@openclimatefix.org",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/openclimatefix/nowcasting_api/blob/main/LICENSE",
    },
)

thirty_minutes = timedelta(minutes=30)


# Dependency
def get_session():
    """Get database settion"""
    connection = DatabaseConnection(url=os.getenv("DB_URL", "not_set"))

    with connection.get_session() as s:
        yield s


@app.get("/")
async def get_api_information():
    """Get information about the API itself"""

    logger.info("Route / has be called")

    return {
        "title": "Nowcasting API",
        "version": version,
        "description": description,
        "documentation": "https://api.nowcasting.io/docs",
    }


@app.get("/v0/forecasts/GB/pv/gsp/{gsp_id}", response_model=Forecast)
async def get_forecasts_for_a_specific_gsp(
    gsp_id, session: Session = Depends(get_session)
) -> Forecast:
    """Get one forecast for a specific GSP id"""

    logger.info(f"Get forecasts for gsp id {gsp_id}")

    if int(os.getenv("FAKE", 0)):
        return create_dummy_gsp_forecast(gsp_id=gsp_id)

    else:
        return get_forecasts_for_a_specific_gsp_from_database(session=session, gsp_id=gsp_id)


@app.get("/v0/forecasts/GB/pv/gsp", response_model=ManyForecasts)
async def get_all_available_forecasts(session: Session = Depends(get_session)) -> ManyForecasts:
    """Get the latest information for all available forecasts"""

    logger.info("Get forecasts for all gsps")
    if int(os.getenv("FAKE", 0)):
        return ManyForecasts(forecasts=[create_dummy_gsp_forecast(gsp_id) for gsp_id in range(10)])
    else:
        return get_forecasts_from_database(session=session)


@app.get("/v0/forecasts/GB/pv/national", response_model=Forecast)
async def get_nationally_aggregated_forecasts() -> Forecast:
    """Get an aggregated forecast at the national level"""

    logger.debug("Get national forecasts")

    return create_dummy_national_forecast()
