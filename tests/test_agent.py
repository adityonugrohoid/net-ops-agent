import pytest
from unittest.mock import MagicMock, patch
from src.agent import analyze_request, execute_tool

def test_analyze_request_tool_call():
    """Tests that agent correctly identifies and returns tool call."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("src.agent.model") as mock_model:
            # Setup mock chat
            mock_chat = MagicMock()
            mock_model.start_chat.return_value = mock_chat
            
            # Setup mock response with function call
            mock_response = MagicMock()
            mock_part = MagicMock()
            mock_fc = MagicMock()
            mock_fc.name = "get_service_health"
            mock_fc.args = {"service_name": "web-api"}
            mock_part.function_call = mock_fc
            mock_response.parts = [mock_part]
            mock_chat.send_message.return_value = mock_response
            
            result = analyze_request("Check the health of web-api")
            
            assert result["type"] == "action"
            assert result["tool"] == "get_service_health"
            assert result["args"]["service_name"] == "web-api"

def test_analyze_request_text_response():
    """Tests that agent returns text response when no tool is needed."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("src.agent.model") as mock_model:
            mock_chat = MagicMock()
            mock_model.start_chat.return_value = mock_chat
            
            # Setup response with no function call
            mock_response = MagicMock()
            mock_response.text = "I can help you with network operations."
            mock_part = MagicMock()
            mock_part.function_call = None
            mock_response.parts = [mock_part]
            mock_chat.send_message.return_value = mock_response
            
            result = analyze_request("What can you do?")
            
            assert result["type"] == "chat"
            assert "network operations" in result["response"]

def test_analyze_request_error_handling():
    """Tests error handling when agent call fails."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("src.agent.model") as mock_model:
            mock_chat = MagicMock()
            mock_model.start_chat.return_value = mock_chat
            
            # Simulate API error
            mock_chat.send_message.side_effect = Exception("API Timeout")
            
            result = analyze_request("Do something")
            
            assert result["type"] == "chat"
            assert "Error interacting with Agent" in result["response"]
            assert "API Timeout" in result["response"]

def test_execute_tool_get_service_health():
    """Tests execution of get_service_health tool."""
    result = execute_tool("get_service_health", {"service_name": "api-gateway"})
    
    assert "service" in result
    assert result["service"] == "api-gateway"
    assert "status" in result
    assert "cpu_usage_percent" in result
    assert "memory_usage_mb" in result

def test_execute_tool_restart_service():
    """Tests execution of restart_service tool."""
    result = execute_tool("restart_service", {"service_name": "web-server", "force": True})
    
    assert result["service"] == "web-server"
    assert result["action"] == "restart"
    assert result["mode"] == "force"
    assert result["status"] == "Success"

def test_execute_tool_restart_service_graceful():
    """Tests graceful restart (default behavior)."""
    result = execute_tool("restart_service", {"service_name": "db-server", "force": False})
    
    assert result["service"] == "db-server"
    assert result["mode"] == "graceful"
    assert result["status"] == "Success"

def test_execute_tool_scale_cluster():
    """Tests execution of scale_cluster tool."""
    result = execute_tool("scale_cluster", {"cluster_id": "prod-cluster", "replicas": 5})
    
    assert result["cluster_id"] == "prod-cluster"
    assert result["current_replicas"] == 5
    assert result["status"] == "Scaled"
    assert "previous_replicas" in result

def test_execute_tool_unknown_tool():
    """Tests error handling for unknown tool names."""
    result = execute_tool("nonexistent_tool", {})
    
    assert "error" in result
    assert "Unknown tool" in result["error"]

def test_execute_tool_invalid_arguments():
    """Tests error handling for invalid tool arguments."""
    # Missing required argument
    result = execute_tool("get_service_health", {})
    
    assert "error" in result
    assert "Tool execution failed" in result["error"]

def test_analyze_request_scale_cluster_inference():
    """Tests that agent correctly infers scale_cluster tool."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("src.agent.model") as mock_model:
            mock_chat = MagicMock()
            mock_model.start_chat.return_value = mock_chat
            
            # Setup mock response
            mock_response = MagicMock()
            mock_part = MagicMock()
            mock_fc = MagicMock()
            mock_fc.name = "scale_cluster"
            mock_fc.args = {"cluster_id": "east-1", "replicas": 10}
            mock_part.function_call = mock_fc
            mock_response.parts = [mock_part]
            mock_chat.send_message.return_value = mock_response
            
            result = analyze_request("Scale east-1 cluster to 10 replicas")
            
            assert result["type"] == "action"
            assert result["tool"] == "scale_cluster"
            assert result["args"]["cluster_id"] == "east-1"
            assert result["args"]["replicas"] == 10

def test_analyze_request_restart_with_force():
    """Tests that agent correctly infers force parameter."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "fake_key"}):
        with patch("src.agent.model") as mock_model:
            mock_chat = MagicMock()
            mock_model.start_chat.return_value = mock_chat
            
            # Setup mock response
            mock_response = MagicMock()
            mock_part = MagicMock()
            mock_fc = MagicMock()
            mock_fc.name = "restart_service"
            mock_fc.args = {"service_name": "payment-api", "force": True}
            mock_part.function_call = mock_fc
            mock_response.parts = [mock_part]
            mock_chat.send_message.return_value = mock_response
            
            result = analyze_request("Restart payment-api immediately")
            
            assert result["type"] == "action"
            assert result["tool"] == "restart_service"
            assert result["args"]["force"] is True

if __name__ == "__main__":
    import sys
    try:
        test_execute_tool_get_service_health()
        print("test_execute_tool_get_service_health passed")
        test_execute_tool_restart_service()
        print("test_execute_tool_restart_service passed")
        test_execute_tool_scale_cluster()
        print("test_execute_tool_scale_cluster passed")
        test_execute_tool_unknown_tool()
        print("test_execute_tool_unknown_tool passed")
        test_execute_tool_invalid_arguments()
        print("test_execute_tool_invalid_arguments passed")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)

