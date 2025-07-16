from fastapi.testclient import TestClient
import pytest
from sqlalchemy import StaticPool
from app.model.models import Product, Order, Log
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.model.database import get_session, engine
import os
from dotenv import load_dotenv

load_dotenv("./.env")

sql_url = os.environ["SQL_TEST_URL"]
connect_args = {}
if "sqlite" in sql_url:
    connect_args = {"check_same_thread": False}
test_engine = create_engine(
    sql_url,
    connect_args=connect_args,
    poolclass=StaticPool,
)

engine = test_engine
SQLModel.metadata.create_all(
    test_engine,
)


def get_test_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def clean_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


os.environ["ENV"] = "DEV"
app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)
