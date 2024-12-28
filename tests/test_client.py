import pytest
from quipclient import QuipClient

def test_client_initialization(quip_client):
    assert quip_client.access_token == "test_token"
    assert quip_client._rate_limit is None
    assert quip_client._company_rate_limit is None

def test_url_construction(quip_client):
    url = quip_client._url("threads/123", count=5)
    assert url == "https://platform.quip.com/1/threads/123?count=5"

def test_clean_params(quip_client):
    cleaned = quip_client._clean(count=5, title="test")
    assert cleaned["count"] == "5"
    assert isinstance(cleaned["title"], bytes)
