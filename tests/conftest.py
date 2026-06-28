import os
import pytest

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:3000")
VALID_ENVS = ("dev", "prod")


@pytest.fixture(params=VALID_ENVS)
def environment(request):
    env = request.param
    if env not in VALID_ENVS:
        pytest.fail(f"Invalid environment: '{env}'. Please choose: {VALID_ENVS}")
    return env
    
@pytest.fixture
def base_url():
    return BASE_URL