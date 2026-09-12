# backend/tests/test_work_orders.py
import uuid

from fastapi.testclient import TestClient


def test_create_and_read_work_order(client: TestClient) -> None:
    location = client.post(
        "/locations", json={"title":"factory1", "coordinates": "45.5,-73.6"}).json()
    
    data = {
        "title": "fix laser scanners",
        "status": "open",
        "location_id": location["id"],
    }

    response = client.post("/work-orders", json=data)
    assert response.status_code == 200
    created = response.json()
    assert created["title"] == data["title"]
    assert created["status"] == data["status"]
    assert created["location_id"] == data["location_id"]
    assert "id" in created

    response = client.get(f"/work-orders/{created['id']}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == created["id"]
    assert fetched["title"] == data["title"]
    assert fetched["location_id"] == data["location_id"]
    

def test_read_work_order_not_found(client: TestClient) -> None:
    response = client.get(f"/work-orders/{uuid.uuid4()}")
    assert response.status_code == 404


def test_create_work_order_invalid(client: TestClient) -> None:
    response = client.post("/work-orders", json={"status": "open"})
    assert response.status_code == 400