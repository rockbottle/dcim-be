# import pytest


def test_get_available_resources(client):
    """
    Tests the resource calculator.
    Matches the specific route found in your app: /usage/my_availble_usage
    """
    # Using the exact path from your registered routes
    response = client.get("/usage/my_availble_usage")

    assert response.status_code == 200
    # Business logic check: ensure the calculator returns the correct keys
    data = response.json()
    assert "available_power" in data
    assert "available_uspace" in data


def test_get_my_usage_details(client):
    """
    Tests /usage/my_details
    """
    response = client.get("/usage/my_details")
    assert response.status_code == 200
    # Matches the 20000 dcpower seeded in conftest.py
    assert response.json()["dcpower"] == 20000


def test_delete_usage_record_logic(client):
    """
    Verifies that you cannot delete usage if inventory exists.
    """
    # 1. Add inventory to consume resources and block deletion
    inv_payload = {
        "device_type": "Switch",
        "device_hostname": "sw-01",
        "device_model": "Gen",
        "device_serial": "S1",
        "rack_name": "R1",
        "rack_unit": 1,
        "rack_uspace": 1,
        "device_power": 100,
        "device_nports": 1,
        "device_sports": 1,
        "power_status": True,
        "device_status": True,
    }
    # Ensure creation is successful first
    create_inv = client.post("/inventory/create", json=inv_payload)
    assert create_inv.status_code == 200

    # 2. Attempt to delete usage record
    response = client.delete("/usage/delete")

    # This should return 400 because inventory exists for this company
    assert response.status_code == 400
    assert "inventory exists" in response.json()["detail"].lower()
