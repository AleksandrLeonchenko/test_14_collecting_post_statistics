from sqlalchemy import Column, Integer, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from datetime import datetime

from sqlalchemy import (TIMESTAMP, Column, Integer, String, Table)

from database import Base, metadata
#
# metadata = MetaData()

task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("link", String),
    Column("created_at", TIMESTAMP, default=datetime.utcnow),
    Column("status", Integer),
    Column("number_of_views", Integer),
)

