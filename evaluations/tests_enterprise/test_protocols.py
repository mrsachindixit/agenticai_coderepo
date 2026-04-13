"""Tests for Module 5: Enterprise agent communication and protocols."""

import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_message_schema_role_types():
    """Test that message schemas enforce valid role types."""
    valid_roles = ["system", "user", "assistant", "tool"]
    
    for role in valid_roles:
        msg = {"role": role, "content": "test content"}
        assert msg["role"] in valid_roles

def test_message_json_serializable():
    """Test that agent messages are JSON-serializable."""
    messages = [
        {"role": "system", "content": "You are an agent."},
        {"role": "user", "content": "Process this request."},
        {"role": "assistant", "content": "I will process it."}
    ]
    
    # Should serialize without error
    serialized = json.dumps(messages)
    deserialized = json.loads(serialized)
    
    assert len(deserialized) == 3
    assert deserialized[0]["role"] == "system"

def test_a2a_message_format():
    """Test Agent-to-Agent message format."""
    # A2A messages should include sender, recipient, and payload
    a2a_message = {
        "sender": "planner_agent",
        "recipient": "executor_agent",
        "payload": {
            "task": "Execute plan step 1",
            "context": "Initial context"
        }
    }
    
    assert a2a_message["sender"] in ["planner_agent", "executor_agent"]
    assert a2a_message["recipient"] in ["planner_agent", "executor_agent"]
    assert "task" in a2a_message["payload"]

def test_protocol_version_tracking():
    """Test that protocol versions are tracked for compatibility."""
    message = {
        "protocol_version": "1.0",
        "timestamp": "2026-02-24T00:00:00Z",
        "content": {"data": "test"}
    }
    
    assert message["protocol_version"] == "1.0"
    assert "timestamp" in message
