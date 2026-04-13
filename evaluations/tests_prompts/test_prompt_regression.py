
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
from utils.ollama_client import generate

def test_definition_contains_agent_keyword():
    out = generate('Define an AI agent in one concise sentence.', temperature=0)
    assert 'agent' in out.lower()
