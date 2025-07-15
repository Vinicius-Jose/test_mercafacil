from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from app.model.models import (
    Order,
    OrderProduct,
    OrderInput,
    OrderOutput,
    OrderProductInput,
    OrderProductOutput,
    Product,
)
from app.controller.product import get_product
from app.database import get_session

router = APIRouter(prefix="/orders", tags=["Orders"])


def sqlmodel_to_order_output(order: Order) -> OrderOutput:
    total_amount = 0
    products = []
    for item in order.products:
        order_product_output = OrderProductOutput(
            id=item.product_id, quantity=item.quantity, price=item.price
        )
        total_amount += order_product_output.price * order_product_output.quantity
        products.append(order_product_output)
    order_output = OrderOutput(
        order_id=order.order_id,
        customer_id=order.customer_id,
        status=order.status,
        created_at=order.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        products=products,
        total_amount=total_amount,
    )
    return order_output


def order_input_to_sqlmodel(order_input: OrderInput, session: Session) -> Order:
    order = Order(customer_id=order_input.customer_id)
    order.products = []
    for item in order_input.products:
        product: Product = get_product(item.id, session)
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The quantity {item.quantity} for product with {product.id} is invalid."
                + f"Need to be lower or equal to quantity available in stock: {product.stock}  stock ",
            )
        product.stock -= item.quantity
        session.add(product)
        session.commit()
        order_products = OrderProduct(
            product_id=product.id,
            order_id=order.order_id,
            quantity=item.quantity,
            price=product.price,
        )
        order.products.append(order_products)
    return order


@router.post("/", response_model=OrderOutput)
def post(
    order_input: OrderInput, session: Session = Depends(get_session)
) -> JSONResponse:
    order = order_input_to_sqlmodel(order_input, session)

    session.add(order)
    session.commit()
    session.refresh(order)

    order_output = sqlmodel_to_order_output(order)
    # TODO Add order to worker
    return JSONResponse(order_output.model_dump(), status_code=status.HTTP_201_CREATED)


@router.get("/", response_model=list[OrderOutput])
def get_orders(session: Session = Depends(get_session)) -> list[OrderOutput]:
    statement = select(Order).order_by(Order.created_at.desc()).limit(20)
    orders = session.exec(statement).all()
    orders_output = []
    for order in orders:
        orders_output.append(sqlmodel_to_order_output(order))
    return orders_output


@router.get("/{id}", response_model=OrderOutput)
def get_order(id: str, session: Session = Depends(get_session)) -> OrderOutput:
    order = session.get(Order, id)
    if order:
        return sqlmodel_to_order_output(order)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id {id} not found"
    )


@router.put("/{id}", response_model=OrderOutput)
def put(
    id: str, order_input: OrderInput, session: Session = Depends(get_session)
) -> OrderOutput:
    order = get_order(id, session)
    order.customer_id = order_input.customer_id
    order_db_products_id = [item.id for item in order.products]
    order_input_products_id = [item.id for item in order_input.products]
    products_deleted = list(set(order_db_products_id) - set(order_input_products_id))
    for product in order_input.products:
        update_order_product(session, order, order_db_products_id, product)
    delete_order_products(session, order, products_deleted)
    order = session.get(Order, id)
    session.commit()
    return sqlmodel_to_order_output(order)


@router.delete("/{id}", response_model=OrderOutput)
def delete(id: str, session: Session = Depends(get_session)) -> JSONResponse:
    order = session.get(Order, id)
    if order:
        session.delete(order)
        session.commit()
        return JSONResponse(
            sqlmodel_to_order_output(order).model_dump(),
            status_code=status.HTTP_204_NO_CONTENT,
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id {id} not found"
    )


def delete_order_products(
    session: Session, order: OrderOutput, products_deleted: list[id]
):
    for deleted in products_deleted:
        product_db: Product = get_product(deleted, session)
        statetment = select(OrderProduct).where(
            OrderProduct.order_id == order.order_id,
            OrderProduct.product_id == product_db.id,
        )
        order_product = session.exec(statetment).first()
        product_db.stock += order_product.quantity
        session.delete(order_product)
        session.add(product_db)
        session.commit()


def update_order_product(
    session: Session,
    order: OrderOutput,
    order_db_products_id: list[int],
    product: OrderProductInput,
) -> None:
    product_db: Product = get_product(product.id, session)
    if product.id in order_db_products_id:
        statetment = select(OrderProduct).where(
            OrderProduct.order_id == order.order_id,
            OrderProduct.product_id == product_db.id,
        )
        order_product_db = session.exec(statetment).first()
        product_db.stock += product.quantity - order_product_db.quantity
        order_product_db.quantity = product.quantity

        session.add(product_db)
        session.add(order_product_db)
        session.commit()
    else:
        order_product = OrderProduct(
            product_id=product.id,
            order_id=order.order_id,
            quantity=product.quantity,
            price=product_db.price,
        )
        session.add(order_product)
        session.commit()
