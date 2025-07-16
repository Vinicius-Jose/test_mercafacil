from multiprocessing import Process, Queue, Event
import time

from sqlmodel import Session

from app.model.database import get_session
from app.model.models import Order


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Worker:

    def __init__(self) -> None:
        self.__queue = Queue()
        self.__process: Process | None = None

    def add_to_queue(self, order_id: int, get_session: callable) -> None:
        self.__queue.put(order_id)
        if not self.__process or not self.__process.is_alive():
            self.__process = Process(
                target=worker_p,
                args=(
                    self.__queue,
                    get_session,
                ),
            )
            self.__process.start()


def worker_p(queue: Queue, get_session: callable) -> None:
    session: Session = next(get_session())
    while not queue.empty():
        order_id: int = queue.get()
        order = session.get(Order, order_id)
        if order.status == "pending":
            order.status = "processing"
            queue.put(order.order_id)
        elif order.status == "processing":
            time.sleep(1)  # Simulate order processing
            order.status = "completed"
        session.add(order)
        session.commit()
