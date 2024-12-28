import os
import pytest
from dotenv import load_dotenv
from quipclient import QuipClient
from datetime import datetime, timedelta

# Load environment variables from ../.env
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

@pytest.fixture(scope="session")
def quip_client(tmp_path_factory):
    """Create a QuipClient instance using API key from environment"""
    api_key = os.getenv("QUIP_API_KEY")
    base_url = os.getenv("QUIP_API_BASE_URL", "https://platform.quip.com")
    
    if not api_key:
        pytest.skip("QUIP_API_KEY environment variable not set")
    
    # Create persistent cache directory
    cache_dir = tmp_path_factory.mktemp("quip_cache")
    
    return QuipClient(
        access_token=api_key,
        base_url=base_url,
        cache_dir=str(cache_dir)
    )

@pytest.fixture(scope="session")
def shared_folder_ids(quip_client):
    """Get shared folder IDs from authenticated user with long TTL cache"""
    # 365 days in seconds
    YEAR_TTL = 365 * 24 * 60 * 60
    
    user = quip_client.get_authenticated_user(cache=True, cache_ttl=YEAR_TTL)
    return user.get("shared_folder_ids", [])
