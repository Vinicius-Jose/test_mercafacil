from dotenv import load_dotenv
import os

load_dotenv("./.env")
os.environ["ENV"] = "DEV"


from typing import Any
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import StaticPool
from app.model.models import Product, Order, Log
from sqlmodel import SQLModel, create_engine, Session
from app.main import app
from app.model.database import get_session
import os
from dotenv import load_dotenv


sql_url = os.environ["SQL_TEST_URL"]
connect_args = {}
if "sqlite" in sql_url:
    connect_args = {"check_same_thread": False}
test_engine = create_engine(
    sql_url,
    connect_args=connect_args,
    poolclass=StaticPool,
)

SQLModel.metadata.create_all(
    test_engine,
)


@pytest.fixture
def clean_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield


client = TestClient(app)
