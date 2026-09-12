import uuid

from fastapi.testclient import TestClient

def test_create_location_and_read_its_work_orders(client: TestClient) -> None:

    location = {
        "title":"factory1",
        "coordinates": "45.5,-73.6"
    }

    work_order_1 = {
        "title": "fix laser scanners",
        "status": "open",
    }

    work_order_2 = {
            "title": "fix laser belt",
            "status": "open",
        }

    work_orders = [work_order_1,work_order_2]

    response = client.post("/locations", json=location)
    assert response.status_code == 200
    created = response.json()
    assert created["title"] == location["title"]
    assert created["coordinates"] == location["coordinates"]
    assert "id" in created

    response = client.get(f"/locations/{created['id']}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == created["id"]
    assert fetched["title"] == created["title"]
    assert fetched["coordinates"] == created["coordinates"]

    for order in work_orders:
        order["location_id"] = created["id"]
        response = client.post("/work-orders", json=order)
        assert response.status_code == 200

    response = client.get(f"/locations/{created['id']}/work-orders")
    assert response.status_code == 200
    fetched_orders = response.json()
    assert len(fetched_orders) == len(work_orders)
    assert {order["title"] for order in fetched_orders} == {
        work_order_1["title"],
        work_order_2["title"],
    }
    assert all(order["location_id"] == created["id"] for order in fetched_orders)


def test_read_location_not_found(client: TestClient) -> None:
    response = client.get(f"/locations/{uuid.uuid4()}")
    assert response.status_code == 404

def test_create_location_invalid(client: TestClient) -> None:
    response = client.post("/locations", json={"title": "factory2"})
    assert response.status_code == 400

def test_read_work_orders_for_unknown_location(client: TestClient) -> None:
    response = client.get(f"/locations/{uuid.uuid4()}/work-orders")
    assert response.status_code == 404
    
