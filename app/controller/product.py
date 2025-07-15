from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from app.model.models import Product, ProductInput
from app.database import get_session

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=Product)
def post(
    product_input: ProductInput, session: Session = Depends(get_session)
) -> JSONResponse:
    product = Product(**product_input.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return JSONResponse(
        product.model_dump(),
        status_code=status.HTTP_201_CREATED,
    )


@router.get("/", response_model=List[Product])
def get_products(session: Session = Depends(get_session)) -> JSONResponse:
    statement = select(Product)
    products = session.exec(statement).all()
    return products


@router.get("/{id}", response_model=Product)
def get_product(id: str, session: Session = Depends(get_session)) -> JSONResponse:
    product = session.get(Product, id)
    if product:
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {id} not found"
    )


@router.put("/{id}", response_model=Product)
def put(
    id: str, product_input: ProductInput, session: Session = Depends(get_session)
) -> JSONResponse:
    product: Product = get_product(id, session)
    product.name = product_input.name
    product.description = product_input.description
    product.price = product_input.price
    product.stock = product_input.stock
    product.category = product_input.category
    session.add(product)
    session.commit()
    return product


@router.delete("/{id}", response_model=Product)
def delete(id: str, session: Session = Depends(get_session)) -> JSONResponse:
    product: Product = get_product(id, session)
    session.delete(product)
    session.commit()
    return JSONResponse(product.model_dump(), status_code=status.HTTP_204_NO_CONTENT)
