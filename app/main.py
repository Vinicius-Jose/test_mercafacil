from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import toml

from app.controller.product import router as product_router
from app.controller.order import router as order_router
from app.database import create_db_and_tables

with open("pyproject.toml", "r") as f:
    config = toml.load(f)
    config: dict = config.get("project")

load_dotenv("./.env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Ecommerce", version=config.get("version"))
app.include_router(product_router)
app.include_router(order_router)
