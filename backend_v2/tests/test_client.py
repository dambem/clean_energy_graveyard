import pytest
from src.clients import AnthropicClient, MessageResponse
from main import AppConfig

@pytest.fixture(scope="module")
def app():
    print('='*60)
    print("Warning - testing on real-clients")
    cfg = AppConfig()    
    return AnthropicClient(api_key=cfg.api_key)

def test_anthropic_client(app):
    response = app.call("What is the capital of France?")

    assert "Paris" in response.text, f"Expected 'Paris' in response, got: {response}"