# кол-во assert 6

import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_login_auth(auth_client, test_reg, test_login):
    response = await auth_client.post("/auth/register", json=test_reg)
    response = await auth_client.post("/auth/login", json=test_login)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_202_ACCEPTED]
    
    invalid_username_data = {**test_login, "username": "ERROR USER)@(*#)()"}
    invalid_response = await auth_client.post("/auth/login", json=invalid_username_data)
    assert invalid_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    incorrect_username_data = {**test_login, "username": "ws"}
    invalid_response = await auth_client.post("/auth/login", json=incorrect_username_data)
    assert invalid_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    
    invalid_password_data = {**test_login, "password": "error"}
    invalid_password_response = await auth_client.post("/auth/login", json=invalid_password_data)
    assert invalid_password_response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
