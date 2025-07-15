from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from app.model.models import Product, Order
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.database import get_session
import os

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


def get_test_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)
