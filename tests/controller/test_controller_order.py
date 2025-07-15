from tests.main import client
from datetime import datetime
from time import sleep

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def insert_products() -> list[dict]:
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
    products = []
    for product in products_input:
        response = client.post("/products", json=product)
        products.append(response.json())
    return products


def test_post() -> None:
    product = insert_products()[0]
    now = datetime.now().date()
    order = {
        "customer_id": "cust123",
        "products": [{"id": product.get("id"), "quantity": 3}],
    }
    response = client.post("/orders", json=order)
    assert response.status_code == 201
    order_response: dict = response.json()
    assert order_response.get("order_id")
    total_amount = sum(
        [item["quantity"] * item["price"] for item in order_response["products"]]
    )
    assert order_response.get("total_amount") == total_amount
    created_at = datetime.strptime(order_response.get("created_at"), DATE_FORMAT)
    assert now == created_at.date()
    response = client.get(f"/products/{product.get('id')}")
    product_response: dict = response.json()
    assert product_response.get("stock") == (
        product.get("stock") - order.get("products")[0].get("quantity")
    )


def test_post_quantity_invalid() -> None:
    product = insert_products()[0]
    order = {
        "customer_id": "cust123",
        "products": [{"id": product.get("id"), "quantity": product.get("stock") + 10}],
    }
    response = client.post("/orders", json=order)
    assert response.status_code == 400


def test_get_orders() -> None:
    product = insert_products()[0]
    for i in range(0, 30):
        order = {
            "customer_id": f"cust{i}",
            "products": [{"id": product.get("id"), "quantity": 1}],
        }
        client.post("/orders", json=order)
        sleep(0.3)  # Sleep to secure that all orders will not be created at same time
    response = client.get("/orders")
    assert response.status_code == 200
    orders: list[dict] = response.json()
    assert len(orders) == 20
    order_1 = orders[0]
    order_2 = orders[-1]
    date_1 = datetime.strptime(order_1.get("created_at"), DATE_FORMAT)
    date_2 = datetime.strptime(order_2.get("created_at"), DATE_FORMAT)
    assert date_1 > date_2


def test_get_order() -> None:
    product = insert_products()[0]
    order = {
        "customer_id": "cust123",
        "products": [{"id": product.get("id"), "quantity": 3}],
    }
    response = client.post("/orders", json=order)
    order_response = response.json()
    response = client.get(f"/orders/{order_response.get('order_id')}")
    assert response.status_code == 200
    order_found = response.json()
    assert order_found.get("order_id") == order_response.get("order_id")


def test_put_add_product_order() -> None:
    products = insert_products()
    order = {
        "customer_id": "cust123",
        "products": [{"id": products[0].get("id"), "quantity": 1}],
    }
    response = client.post("/orders", json=order)
    order_response = response.json()
    order["products"].append({"id": products[1].get("id"), "quantity": 1})
    response = client.put(f"/orders/{order_response.get('order_id')}", json=order)
    assert response.status_code == 200
    response = client.get(f"/orders/{order_response.get('order_id')}")
    order_response = response.json()
    assert len(order_response.get("products")) == len(order["products"])


def test_put_remove_product_order() -> None:
    products = insert_products()
    order = {
        "customer_id": "cust123",
        "products": [
            {"id": products[0].get("id"), "quantity": 1},
            {"id": products[1].get("id"), "quantity": 1},
        ],
    }
    response = client.post("/orders", json=order)
    order_response = response.json()
    del order["products"][1]
    response = client.put(f"/orders/{order_response.get('order_id')}", json=order)
    assert response.status_code == 200
    response = client.get(f"/orders/{order_response.get('order_id')}")
    order_response = response.json()
    assert len(order_response.get("products")) == len(order["products"])


def test_delete() -> None:
    product = insert_products()[0]
    order = {
        "customer_id": "cust123",
        "products": [{"id": product.get("id"), "quantity": 3}],
    }
    response = client.post("/orders", json=order)
    order = response.json()
    response = client.delete(f"/orders/{order.get('order_id')}")
    assert response.status_code == 204
    response = client.get(f"/orders/{order.get('order_id')}")
    assert response.status_code == 404


def test_delete_not_found() -> None:
    response = client.delete("/orders/5")
    assert response.status_code == 404
