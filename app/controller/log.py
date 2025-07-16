import logging
from fastapi import Request
from fastapi.concurrency import iterate_in_threadpool
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from time import time
import os
from starlette.background import BackgroundTask


from app.model.database import get_session
from app.model.models import Log

level = os.environ.get("LOG_LEVEL", "INFO")
try:
    level = getattr(logging, level.upper())
except Exception:
    level = logging.INFO
logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> StreamingResponse:
        created_at = datetime.now()
        start = time()
        request_body = await request.body()
        request_body = request_body.decode("utf-8")

        logger.info(f"Request: {request.method} {request.url}")
        logger.debug(
            f"Request Made by: {request.client.host} -  Headers {request.headers} -  Body: {request_body}"
        )
        response: StreamingResponse = await call_next(request)

        process_time = time() - start
        logger.info(
            f"Response: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s"
        )

        response_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        response_body = (b"".join(response_body)).decode("utf-8")

        response.background = BackgroundTask(
            self.write_log_db,
            request,
            request_body,
            response_body,
            response.status_code,
            process_time,
            created_at,
        )
        return response

    async def write_log_db(
        self,
        request: Request,
        request_body: dict,
        response_body: dict,
        status_code: int,
        process_time: float,
        created_at: datetime,
    ):
        session: Session = next(get_session())

        log = Log(
            ip_address=request.client.host,
            path=request.url.path,
            method=request.method,
            status_code=status_code,
            request_body=request_body,
            response_body=response_body,
            query_params=request.url.query,
            process_time=process_time,
            created_at=created_at,
        )
        session.add(log)
        session.commit()
