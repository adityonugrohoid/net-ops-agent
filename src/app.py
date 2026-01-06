import streamlit as st
import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import analyze_request, execute_tool

# --- CSS Styling ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(
    page_title="Net-Ops Executor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None

# --- Main App ---
# --- UI Header ---
st.title("🤖 Net-Ops Executor Agent")
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("System Status")
    st.success("Agent Online")
    st.info("Model: gemini-2.0-flash-lite")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.pending_action = None
        st.rerun()

# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Identify if content is JSON (likely an action result) for pretty printing
        content = message["content"]
        try:
            # simple check if it looks like a dict usage result
            if isinstance(content, dict):
                st.json(content)
            else:
                st.markdown(content)
        except:
            st.markdown(content)

# --- Safety Widget (Human-in-the-Loop) ---
if st.session_state.pending_action:
    action = st.session_state.pending_action
    
    with st.container(border=True):
        st.warning("⚠️ **APPROVAL REQUIRED**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Action:** `{action['tool']}`")
            st.markdown("**Parameters:**")
            st.json(action['args'])
        
        with col2:
            st.markdown("### Authorize?")
            if st.button("✅ Approve", use_container_width=True):
                # Execute Action
                with st.spinner(f"Executing {action['tool']}..."):
                    result = execute_tool(action['tool'], action['args'])
                
                # Append Result to History
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Executed `{action['tool']}`.\n\nResult:"
                })
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result # store result as distinct message content for flexibility
                })
                
                # Clear Pending
                st.session_state.pending_action = None
                st.rerun()
                
            if st.button("❌ Reject", use_container_width=True):
                # Append Rejection to History
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Action `{action['tool']}` was rejected by the operator."
                })
                
                # Clear Pending
                st.session_state.pending_action = None
                st.rerun()

# --- Chat Input ---
# Only show chat input if no pending action to prevent race conditions or confusion
if not st.session_state.pending_action:
    if prompt := st.chat_input("Enter operational command..."):
        # Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Analyze Request
        with st.spinner("Analyzing request..."):
            response = analyze_request(prompt, st.session_state.messages)
            
        # Handle Response
        if response["type"] == "chat":
            st.session_state.messages.append({"role": "assistant", "content": response["response"]})
            with st.chat_message("assistant"):
                st.markdown(response["response"])
                
        elif response["type"] == "action":
            st.session_state.pending_action = response
            st.rerun()
