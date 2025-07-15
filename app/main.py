from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.concurrency import asynccontextmanager
import toml

from app.controller.product import router as product_router
from app.controller.order import router as order_router
from app.database import create_db_and_tables, get_session
from app.log import LoggingMiddleware

with open("pyproject.toml", "r") as f:
    config = toml.load(f)
    config: dict = config.get("project")

load_dotenv("./.env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Ecommerce",
    version=config.get("version"),
    dependencies=[Depends(get_session)],
)
app.include_router(product_router)
app.include_router(order_router)

app.add_middleware(LoggingMiddleware)
