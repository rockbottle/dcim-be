import pytest
import time


@pytest.mark.asyncio
async def test_extended_lifecycle_flow(async_client):
    ac = async_client
    unique_suffix = int(time.time())
    test_user = f"admin_{unique_suffix}"
    test_pass = "SecurePassword123!"
    new_pass = "UpdatedPassword456!"

    # --- 1. SETUP: Register and Login ---
    reg_resp = await ac.post(
        "/user/create",
        json={
            "username": test_user,
            "email": f"{test_user}@test.com",
            "password": test_pass,
            "company_name": f"Corp_{unique_suffix}",
        },
    )
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"

    login_resp = await ac.post("/token", data={"username": test_user, "password": test_pass})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- 2. USAGE UPDATE ---
    # Create initial usage
    await ac.post("/usage/create", json={"dcpower": 1000, "uspace": 10, "nport": 10, "sport": 10}, headers=headers)

    # Update usage - Sending full payload to satisfy potential Pydantic/Business logic constraints
    usage_update = await ac.put(
        "/usage/update", json={"dcpower": 2000, "uspace": 100, "nport": 100, "sport": 100}, headers=headers
    )
    assert usage_update.status_code == 200, f"Usage update failed: {usage_update.text}"

    # --- 3. INVENTORY UPDATE & DELETE ---
    inv_resp = await ac.post(
        "/inventory/create",
        json={
            "device_type": "Switch",
            "device_hostname": "sw-01",
            "device_model": "C9300",
            "device_serial": f"SN-{unique_suffix}",
            "rack_name": "R1",
            "rack_unit": 1,
            "rack_uspace": 1,
            "device_power": 100,
            "device_nports": 48,
            "device_sports": 4,
            "power_status": True,
            "device_status": True,
        },
        headers=headers,
    )

    assert inv_resp.status_code == 200, f"Inventory creation failed: {inv_resp.text}"

    # Robustly get the ID (ensuring it's an integer)
    resp_data = inv_resp.json()
    device_id = resp_data.get("id")
    assert device_id is not None, f"Expected 'id' in response, got: {resp_data}"

    # Update - ID passed as query parameter based on error log
    update_resp = await ac.put(
        "/inventory/update/",
        params={"id": int(device_id)},
        json={
            "device_type": "Switch",
            "device_hostname": "sw-01-updated",
            "device_model": "C9300",
            "device_serial": f"SN-{unique_suffix}",
            "rack_name": "R1",
            "rack_unit": 1,
            "rack_uspace": 1,
            "device_power": 100,
            "device_nports": 24,
            "device_sports": 4,
            "power_status": True,
            "device_status": True,
        },
        headers=headers,
    )
    assert update_resp.status_code == 200, f"Inventory update failed: {update_resp.text}"

    # Delete
    del_resp = await ac.delete("/inventory/delete", params={"id": int(device_id)}, headers=headers)
    assert del_resp.status_code == 200, f"Delete failed: {del_resp.text}"

    # --- 4. USER UPDATE & PASSWORD CHANGE ---
    # Update Email
    user_upd = await ac.put("/user/update", json={"email": "new_email@test.com"}, headers=headers)
    assert user_upd.status_code == 200, f"User email update failed: {user_upd.text}"

    # Password Change
    pass_resp = await ac.put("/user/update", json={"password": new_pass}, headers=headers)
    assert pass_resp.status_code == 200, f"User password update failed: {pass_resp.text}"

    # Verify Login with NEW password
    new_login = await ac.post("/token", data={"username": test_user, "password": new_pass})
    assert new_login.status_code == 200, f"Could not login with new password: {new_login.text}"
