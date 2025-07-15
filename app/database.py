from sqlmodel import SQLModel, Session
from app.model.models import Product, Order
from fastapi import Depends
import os
from typing import Annotated
from sqlalchemy import create_engine


sql_url = os.environ["SQL_URL"]
connect_args = {}
if "sqlite" in sql_url:
    connect_args = {"check_same_thread": False}
engine = create_engine(
    sql_url, pool_pre_ping=True, pool_recycle=1800, connect_args=connect_args
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
