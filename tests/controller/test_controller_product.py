from httpx import Response
from tests.main import client, clean_db
from app.model.models import ProductInput


def test_post_product() -> None:
    product = {
        "name": "Lays",
        "description": "Potato chips",
        "price": 10,
        "stock": 50,
        "category": "Food",
    }
    response: Response = client.post("/products", json=product)
    assert response.status_code == 201
    product = response.json()
    assert product.get("id")


def test_get_all_products(clean_db) -> None:
    # This Test need to be executed separeted,
    # because the table product need to be empty
    products_input = [
        {
            "name": "Lays",
            "description": "Potato chips",
            "price": 10,
            "stock": 50,
            "category": "Food",
        },
        {
            "name": "Xbox Series S",
            "description": "Microsoft Console",
            "price": 2200,
            "stock": 10,
            "category": "Video Game",
        },
    ]
    for product in products_input:
        client.post("/products", json=product)
    response: Response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == len(products_input)


def test_get_product() -> None:
    product = {
        "name": "Lays",
        "description": "Potato chips",
        "price": 10,
        "stock": 50,
        "category": "Food",
    }
    response: Response = client.post("/products", json=product)
    product = response.json()
    response: Response = client.get(f"/products/{product.get('id')}")
    assert response.status_code == 200
    product_found = response.json()
    assert product_found == product


def test_get_product_not_found() -> None:
    response: Response = client.get("/products/test")
    assert response.status_code == 404


def test_put_product() -> None:
    product_input = {
        "name": "Lays",
        "description": "Potato chips",
        "price": 10,
        "stock": 50,
        "category": "Food",
    }
    response: Response = client.post("/products", json=product_input)
    product = response.json()
    product_input["name"] = "Elma Chips"
    product_input["description"] = "Famous Potato chips"
    product_input["price"] = 15
    product_input["stock"] = 10

    response: Response = client.put(
        f"/products/{product.get('id')}", json=product_input
    )
    assert response.status_code == 200
    response: Response = client.get(f"/products/{product.get('id')}")
    assert response.status_code == 200
    product_found: dict = response.json()
    assert product_found.get("name") == product_input["name"]
    assert product_found.get("description") == product_input["description"]
    assert product_found.get("price") == product_input["price"]
    assert product_found.get("stock") == product_input["stock"]


def test_put_product_not_found() -> None:
    product_input = {
        "name": "Lays",
        "description": "Potato chips",
        "price": 10,
        "stock": 50,
        "category": "Food",
    }
    response: Response = client.put("/products/test", json=product_input)
    assert response.status_code == 404


def test_delete_product() -> None:
    product_input = {
        "name": "Lays",
        "description": "Potato chips",
        "price": 10,
        "stock": 50,
        "category": "Food",
    }
    response: Response = client.post("/products", json=product_input)
    product: dict = response.json()
    response: Response = client.delete(f"/products/{product.get('id')}")
    assert response.status_code == 204
    response: Response = client.get(f"/products/{product.get('id')}")
    assert response.status_code == 404


def test_delete_product_not_found() -> None:
    response: Response = client.delete("/products/test")
    assert response.status_code == 404
