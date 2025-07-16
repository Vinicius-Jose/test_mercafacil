from typing import Any
from sqlmodel import SQLModel, Session
from app.model.models import Product, Order, Log

import os

from sqlalchemy import StaticPool, create_engine


ENGINE = None
SQL_URL = os.environ["SQL_URL"]
DEV_MODE = os.environ.get("ENV").lower() == "dev"
if DEV_MODE:
    SQL_URL = os.environ["SQL_TEST_URL"]


def get_engine() -> Any:
    global ENGINE
    if ENGINE:
        return ENGINE

    connect_args = {}
    if "sqlite" in SQL_URL:
        connect_args = {"check_same_thread": False}
    if DEV_MODE:
        ENGINE = create_engine(
            SQL_URL,
            connect_args=connect_args,
            poolclass=StaticPool,
        )
    else:
        ENGINE = create_engine(
            SQL_URL,
            pool_pre_ping=True,
            pool_recycle=1800,
            connect_args=connect_args,
        )
    return ENGINE


def create_db_and_tables():
    SQLModel.metadata.create_all(get_engine())


def get_session():
    with Session(get_engine()) as session:
        yield session
