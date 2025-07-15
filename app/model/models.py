import uuid
from sqlmodel import Relationship, SQLModel, Field, Column, JSON
from datetime import datetime


class ProductInput(SQLModel, table=False):
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    price: float = Field(nullable=False, gt=0)
    stock: int = Field(nullable=False, ge=0)
    category: str = Field(nullable=False)


class Product(ProductInput, table=True):
    id: str = Field(
        nullable=False, primary_key=True, default_factory=lambda: str(uuid.uuid4())
    )


class OrderProductInput(SQLModel, table=False):
    id: str = Field(foreign_key="product.id", nullable=False)
    quantity: int = Field(nullable=False, gt=0)


class OrderInput(SQLModel, table=False):
    customer_id: str = Field(nullable=False)
    products: list["OrderProductInput"]


class OrderProduct(SQLModel, table=True):
    product_id: str = Field(foreign_key="product.id", nullable=False, primary_key=True)
    order_id: str = Field(
        foreign_key="order.order_id", nullable=False, primary_key=True
    )
    quantity: int = Field(nullable=False)
    price: float = Field(default=None)


class Order(SQLModel, table=True):
    order_id: str = Field(
        nullable=False, primary_key=True, default_factory=lambda: str(uuid.uuid4())
    )
    customer_id: str = Field(nullable=False)
    products: list["OrderProduct"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
    status: str = Field(nullable=False, default="pending")
    created_at: datetime = Field(nullable=False, default_factory=datetime.now)


class OrderProductOutput(SQLModel, table=False):
    id: str = Field(nullable=False)
    quantity: int = Field(nullable=False)
    price: float = Field(default=None)


class OrderOutput(SQLModel, table=False):
    order_id: str = Field(nullable=False)
    customer_id: str = Field(nullable=False)
    products: list["OrderProductOutput"]
    total_amount: float = Field(default=None)
    status: str = Field(nullable=False)
    created_at: str = Field(nullable=False)


class Log(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    ip_address: str = Field(nullable=False)
    path: str = Field(nullable=False)
    method: str = Field(nullable=True)
    status_code: int = Field(nullable=False)
    request_body: str = Field(default=None, sa_column=Column(JSON))
    response_body: str = Field(default=None, sa_column=Column(JSON))
    query_params: dict | None = Field(default=None, sa_column=Column(JSON))
    process_time: float
    created_at: datetime = Field(nullable=False, default_factory=datetime.now)
