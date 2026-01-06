import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict, Any, Union
from src.tools import get_service_health, restart_service, scale_cluster

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Initialize Model with Tools
tools_list = [get_service_health, restart_service, scale_cluster]
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-lite',
    tools=tools_list
)

def analyze_request(user_input: str, chat_history: List[Dict[str, str]] = []) -> Dict[str, Any]:
    """
    Analyzes the user's request using Gemini and determines the next step.
    
    Args:
        user_input (str): The natural language command from the user.
        chat_history (list): Previous chat content (not fully utilized in this simple stateless pass, 
                             but ready for expansion).

    Returns:
        dict: A dictionary representing the decision.
            - If a tool call is recommended:
              {'type': 'action', 'tool': 'tool_name', 'args': {arg_dict}}
            - If a text response is generated:
              {'type': 'chat', 'response': 'text_content'}
    """
    try:
        # Start a chat session (stateless for this function call for simplicity, 
        # but could pass history if formatted correctly)
        chat = model.start_chat(enable_automatic_function_calling=False)
        
        # Send message
        response = chat.send_message(user_input)
        
        # Check for function call
        # Gemini 2.0 returns function calls in parts
        for part in response.parts:
            if part.function_call:
                fc = part.function_call
                return {
                    "type": "action",
                    "tool": fc.name,
                    "args": dict(fc.args)
                }
        
        # Fallback to text
        return {
            "type": "chat",
            "response": response.text
        }
        
    except Exception as e:
        return {
            "type": "chat",
            "response": f"Error interacting with Agent: {str(e)}"
        }

def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    """
    Executes the specified tool with the provided arguments.

    Args:
        tool_name (str): The name of the function to call.
        tool_args (dict): The arguments to pass to the function.

    Returns:
        Any: The result of the function call.
    """
    # Map string names to actual functions
    tool_map = {
        "get_service_health": get_service_health,
        "restart_service": restart_service,
        "scale_cluster": scale_cluster
    }
    
    if tool_name not in tool_map:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        # Extract function
        func = tool_map[tool_name]
        # execute
        return func(**tool_args)
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
