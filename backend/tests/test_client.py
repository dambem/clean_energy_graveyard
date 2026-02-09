import pytest
from src.clients import AnthropicClient
from main import AppConfig, NimbyAgent
from src.processors.repd_processor import REPDProcessor

@pytest.fixture(scope="module")
def app():
    print('='*60)
    print("Warning - testing on real-clients")
    cfg = AppConfig()    
    processor = REPDProcessor()
    client = AnthropicClient(api_key=cfg.api_key)
    agent = NimbyAgent(client=client, processor=processor)
    return agent

def test_context_run(app):
    response = app.run(max_values=1)
    _, test = response[0]
    
    assert 'certainty' in test.certainty_meta 

def test_specific_context(app):
    context = "solar energy project, cancelled in 2001"
    response = app.run_singular(context)
    assert 'solar' in response.certainty_meta
    assert '2001' in response.certainty_meta

