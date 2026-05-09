# import pytest


def test_create_inventory_device(client):
    """
    Route: /inventory/create
    """
    payload = {
        "device_type": "Switch",
        "device_hostname": "core-sw-01",
        "device_model": "Cisco Catalyst 9300",
        "device_serial": "SN123456789",
        "rack_name": "Rack-A7",
        "rack_unit": 10,
        "rack_uspace": 1,
        "device_power": 350,
        "device_nports": 48,
        "device_sports": 4,
        "power_status": True,
        "device_status": True,
    }
    response = client.post("/inventory/create", json=payload)
    assert response.status_code == 200
    assert response.json()["device_hostname"] == "core-sw-01"


def test_get_my_inventory(client):
    """
    Tests /inventory/my_details.
    We must create a device first because the logic raises a 404 if the list is empty.
    """
    # 1. Setup: Create at least one device so the DB isn't empty
    payload = {
        "device_type": "Switch",
        "device_hostname": "seed-device",
        "device_model": "Generic",
        "device_serial": "SEED123",
        "rack_name": "Rack-A1",
        "rack_unit": 1,
        "rack_uspace": 1,
        "device_power": 100,
        "device_nports": 1,
        "device_sports": 1,
        "power_status": True,
        "device_status": True,
    }
    client.post("/inventory/create", json=payload)

    # 2. Now call the GET details - it should return 200 now
    response = client.get("/inventory/my_details")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["device_hostname"] == "seed-device"


def test_update_inventory_device(client):
    """
    Route: /inventory/update/
    Note: The trailing slash is MANDATORY as per your route list.
    """
    # 1. Setup - Create device
    payload = {
        "device_type": "Router",
        "device_hostname": "test-router",
        "device_model": "Generic",
        "device_serial": "ABC1234",
        "rack_name": "Rack-B1",
        "rack_unit": 5,
        "rack_uspace": 1,
        "device_power": 100,
        "device_nports": 24,
        "device_sports": 2,
        "power_status": True,
        "device_status": True,
    }
    create_resp = client.post("/inventory/create", json=payload)
    device_id = create_resp.json()["id"]

    # 2. Update logic
    update_payload = {"device_hostname": "Updated-Router"}
    # Using query param 'id' and trailing slash after 'update'
    response = client.put(f"/inventory/update/?id={device_id}", json=update_payload)
    assert response.status_code == 200


def test_delete_inventory_device(client):
    """
    Route: /inventory/delete
    """
    # 1. Setup - Create device
    payload = {
        "device_type": "Server",
        "device_hostname": "to-delete",
        "device_model": "Generic",
        "device_serial": "DEL-123",
        "rack_name": "Rack-C1",
        "rack_unit": 1,
        "rack_uspace": 1,
        "device_power": 500,
        "device_nports": 2,
        "device_sports": 0,
        "power_status": True,
        "device_status": True,
    }
    create_resp = client.post("/inventory/create", json=payload)
    device_id = create_resp.json()["id"]

    # 2. Delete logic
    response = client.delete(f"/inventory/delete?id={device_id}")
    assert response.status_code == 200
