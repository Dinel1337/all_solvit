# кол-во assert 4

import pytest

@pytest.mark.asyncio
async def test_auth_flow(auth_client_setup):
    r1 = await auth_client_setup.get("/users/me")
    assert r1.status_code == 200
    assert r1.json()["success"] is True

    r2 = await auth_client_setup.post("/auth/logout")
    assert r2.status_code == 204

    r3 = await auth_client_setup.get("/users/me")
    assert r3.status_code == 401