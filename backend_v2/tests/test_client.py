import pytest
from src.clients import AnthropicClient
from main import AppConfig, NimbyAgent

@pytest.fixture(scope="module")
def app():
    print('='*60)
    print("Warning - testing on real-clients")
    cfg = AppConfig()    
    client = AnthropicClient(api_key=cfg.api_key)
    agent = NimbyAgent(client=client)
    return agent

def test_context_run(app):
    response = app.run(max_values=1)
    _, test = response[0]
    
    assert 'certainty' in test.certainty_meta 

