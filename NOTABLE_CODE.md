# Notable Code: Net-Ops Agent

This document highlights key code sections that demonstrate the technical strengths and architectural patterns implemented in this agentic AI system.

## Overview

Net-Ops Agent is an autonomous agentic AI system that translates natural language commands into safe, deterministic Python function calls. The system demonstrates sophisticated safety patterns including reasoning-action separation, human-in-the-loop approval gates, and deterministic function calling.

---

## 1. Reasoning-Action Separation Pattern

**File:** `src/agent.py`  
**Lines:** 22-67

The system implements clear separation between reasoning (LLM decides which tool) and execution (Python function runs only after approval).

```python
def analyze_request(user_input: str, chat_history: List[Dict[str, str]] = []) -> Dict[str, Any]:
    """
    Analyzes the user's request using Gemini and determines the next step.
    """
    try:
        # Start a chat session with automatic function calling DISABLED
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
```

**Why it's notable:**
- `enable_automatic_function_calling=False` prevents automatic execution
- Returns structured action request instead of executing immediately
- Clear separation: reasoning returns action, execution happens separately
- Type hints provide compile-time safety

---

## 2. Approval Gate with Persistent Session State

**File:** `src/app.py`  
**Lines:** 37-111

The approval gate uses Streamlit session state to persist pending actions across UI refreshes and network lags.

```python
# Initialize session state
if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

# Check for pending action
if st.session_state.pending_action:
    action = st.session_state.pending_action
    
    st.warning("⚠️ **APPROVAL REQUIRED**")
    st.markdown("### Pending Action")
    st.markdown(f"**Action:** `{action['tool']}`")
    st.markdown("**Arguments:**")
    st.json(action['args'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Approve", type="primary", use_container_width=True):
            # Execute Action
            with st.spinner(f"Executing {action['tool']}..."):
                result = execute_tool(action['tool'], action['args'])
            
            st.session_state.pending_action = None
            
    with col2:
        if st.button("❌ Reject", use_container_width=True):
            st.session_state.pending_action = None
```

**Why it's notable:**
- Session state persists across page refreshes
- Clear approval UI with structured action display
- Prevents accidental execution from state loss
- Explicit approve/reject buttons with clear visual indicators

---

## 3. Deterministic Function Calling

**File:** `src/agent.py`  
**Lines:** 15-20

The system uses native function calling with a pre-defined toolbelt, preventing code generation.

```python
# Initialize Model with Tools
tools_list = [get_service_health, restart_service, scale_cluster]
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-lite',
    tools=tools_list
)
```

**File:** `src/tools.py`  
**Lines:** Tool definitions with type hints

```python
def get_service_health(service_name: str) -> Dict[str, Any]:
    """
    Retrieves the health status of a service.
    
    Args:
        service_name: Name of the service to check
        
    Returns:
        Dictionary with service health information
    """
    # Implementation...
```

**Why it's notable:**
- Pre-defined toolbelt limits possible actions
- No code generation capability - only function calling
- Type hints ensure argument validation
- LLM can only select from approved tools

---

## 4. Tool Execution with Validation

**File:** `src/agent.py`  
**Lines:** 69-96

Tool execution includes validation and error handling, ensuring safe function calls.

```python
def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> Any:
    """
    Executes the specified tool with the provided arguments.
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
```

**Why it's notable:**
- Tool name validation before execution
- Safe function mapping prevents arbitrary code execution
- Error handling with structured error responses
- Type-safe argument passing with `**tool_args`

---

## Architecture Highlights

### Safety Architecture

1. **Tool Definition**: Pre-defined functions with type hints
2. **Reasoning Phase**: LLM selects tool and arguments
3. **Approval Gate**: Human authorization required
4. **Execution Phase**: Validated function call

### Design Patterns Used

1. **Reasoning-Action Separation**: Clear boundary between LLM reasoning and execution
2. **Human-in-the-Loop Pattern**: Mandatory approval for all actions
3. **Deterministic Tool Use**: Function calling prevents code generation
4. **State Persistence Pattern**: Session state maintains approval gates

---

## Technical Strengths Demonstrated

- **Safety First**: Multiple layers of protection (toolbelt, approval, validation)
- **State Management**: Persistent session state for reliable approval gates
- **Type Safety**: Python type hints ensure argument correctness
- **Error Resilience**: Comprehensive error handling at each stage
- **Auditability**: All actions logged and tracked
