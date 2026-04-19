import pytest
from tests.utils import loop_request

@pytest.mark.asyncio
async def test_muscle(api_tracker_setup, add_hash):
    test_cases = {
        '@@zalupa': 422,
        '123zalupa': 422,
        '__': 422,
        '': 422,
        " 22 2 2 ": 422,
        "Грудь": 201,
        "СисичКИ": 201,
    }
    
    await loop_request(api_tracker_setup, "/exercises/muscle/", add_hash, test_cases, parametr='name')