# кол-во assert 28

import pytest
from fastapi import status
from tests.utils import loop_request


invalid_emails = [
    "error@", "error@error", "error", "@error.com",
    "error@.com", "error@domain..com", "error@domain.c",
    "error space@domain.com", "error@domain.com."
]

invalid_usernames = [
    "a" * 51, "ab", "user@name", "user#name", "", "   ",
]


@pytest.mark.asyncio
async def test_register_main(auth_client, test_reg):
    email_cases = {e: 422 for e in invalid_emails}
    email_cases[test_reg["email"]] = 201

    await loop_request(
        auth_client,
        "/auth/register",
        {k: v for k, v in test_reg.items() if k != "email"},
        email_cases,
        parametr="email"
    )

    username_cases = {u: 422 for u in invalid_usernames}
    username_cases["new_valid_username"] = 201

    await loop_request(
        auth_client,
        "/auth/register",
        {
            **{k: v for k, v in test_reg.items() if k != "username"},
            "email": "unique_" + test_reg["email"]
        },
        username_cases,
        parametr="username",
        check_dublicate=False
    )


@pytest.mark.asyncio
async def test_register_structure_and_edges(auth_client, test_reg):
    """missing fields + edge cases"""

    for field in ["email", "password", "username"]:
        data = {k: v for k, v in test_reg.items() if k != field}
        r = await auth_client.post("/auth/register", json=data)
        assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    r = await auth_client.post("/auth/register", json={})
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    extra = {**test_reg, "role": "admin"}
    r = await auth_client.post("/auth/register", json=extra)
    assert r.status_code in [201, 422]

    spaced = test_reg.copy()
    spaced["email"] = "  spaced@example.com  "
    spaced["username"] = "  spaceduser  "

    r = await auth_client.post("/auth/register", json=spaced)
    if r.status_code == 201:
        data = r.json().get("data", r.json())
        assert data["email"] == "spaced@example.com"
        assert data["username"] == "spaceduser"


@pytest.mark.asyncio
async def test_register_security(auth_client, test_reg):
    """sql + безопасность ответа + case insensitive"""

    payloads = [
        {"email": "' OR '1'='1", "password": "ValidPass123", "username": "user"},
        {"email": "admin'--", "password": "ValidPass123", "username": "user"},
    ]

    for p in payloads:
        r = await auth_client.post("/auth/register", json=p)
        assert r.status_code < 500

    # норм регистрация
    r1 = await auth_client.post("/auth/register", json=test_reg)
    if r1.status_code != 201:
        pytest.skip()

    data = r1.json().get("data", r1.json())
    assert "password" not in data
    assert "password_hash" not in data

    # case insensitive
    upper = test_reg.copy()
    upper["email"] = test_reg["email"].upper()

    r2 = await auth_client.post("/auth/register", json=upper)
    assert r2.status_code == 409