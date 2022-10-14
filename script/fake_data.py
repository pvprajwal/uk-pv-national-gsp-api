"""
Fill database with fake data, so we can run this locally and the front end works

This is useful for when running the api locally with the front end

need to fill the following tables
1. forecast historic with forecast values
2. gsp yield with in-day and day-after amounts
3. a warning status of this is fake data
"""

from nowcasting_datamodel.connection import DatabaseConnection
from nowcasting_datamodel.fake import make_fake_forecasts, make_fake_gsp_yields
from nowcasting_datamodel.models.models import StatusSQL
from datetime import datetime, timezone
import os

now = datetime.now(tz=timezone.utc)

connection = DatabaseConnection(url=os.getenv("DB_URL", "not_set"))

with connection.get_session() as session:

    # 1. make fake forecasts
    make_fake_forecasts(gsp_ids=range(0, 317), session=session, t0_datetime_utc=now)

    # 2. make gsp yields
    make_fake_gsp_yields(gsp_ids=range(0, 317), session=session, t0_datetime_utc=now)

    # 3. make status
    status = StatusSQL(status="warning", message="this is all fake data")

    session.add(status)
    session.commit()
