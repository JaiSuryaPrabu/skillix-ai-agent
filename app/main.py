# ------ main.py ------ #
import sys
import os
import json
import streamlit as st

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.runners import InMemoryRunner
from google.genai import types

# Your existing agent logic
from agents.orchestrator import create_orchestrator_agent


# --------- Constants --------- #
APP_NAME = "Skillix AI"
USER_ID = "student_01"
SESSION_ID = "session_01"


# --------- Orchestrator + Runner (created once) --------- #
@st.cache_resource
def get_runner() -> InMemoryRunner:
    orchestrator_agent = create_orchestrator_agent()
    return InMemoryRunner(agent=orchestrator_agent, app_name=APP_NAME)

runner = get_runner()


# --------- Streamlit Page Setup --------- #
st.set_page_config(
    page_title="Skillix AI",
    page_icon="🤖",
    layout="centered",
)


# ---------- Custom CSS (Same beautiful style as Old UI) ----------
st.markdown(
    """
<style>
    .block-container {
        max-width: 900px;
        margin: auto;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* Title row */
    .skillix-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        margin-bottom: 0.25rem;
    }
    .skillix-header-icon {
        font-size: 2.3rem;
    }
    .skillix-header-text {
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .skillix-subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Chat card */
    .chat-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
        border: 1px solid #e5e7eb;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .input-hint {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-top: 0.4rem;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ---------- Header ----------
st.markdown(
    """
<div class="skillix-header">
  <div class="skillix-header-icon">🤖</div>
  <div class="skillix-header-text">Skillix AI</div>
</div>
<div class="skillix-subtitle">
  Chat interface connected to the Skillix orchestrator.
</div>
""",
    unsafe_allow_html=True,
)


# --------- Session State for Chat History --------- #
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# --------- Top Row: Info + Reset Button --------- #
col_info, col_reset = st.columns([4, 1])

with col_info:
    st.markdown(
        "Chat with Skillix — ask questions, answer prompts, and get evaluated in real time."
    )

with col_reset:
    if st.button("🔁 Reset chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()


# --------- Enhanced extract_text_from_result (compatible with InMemoryRunner) --------- #
def extract_text_from_result(result) -> str:
    if isinstance(result, list):
        text_parts = []
        for item in result:
            if hasattr(item, "is_final_response") and item.is_final_response():
                if hasattr(item, "content") and item.content and item.content.parts:
                    for part in item.content.parts:
                        if hasattr(part, "text") and part.text:
                            txt = part.text.strip()
                            if txt and len(txt) > 5:
                                if not any(noise in txt for noise in ["<ctrl", "print(default_api", "Tool call", "DEBUG"]):
                                    text_parts.append(txt)
        return "\n".join(text_parts) or "I'm thinking..."

    if hasattr(result, "content"):
        result = result.content

    if isinstance(result, types.GenerateContentResponse):
        try:
            return result.text or ""
        except ValueError:
            return "No text content generated (possibly blocked)."

    if isinstance(result, types.Content):
        return "".join(part.text for part in (result.parts or []) if part.text)

    if isinstance(result, types.Part):
        return result.text or ""

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        for key in ("text", "output_text", "message", "output"):
            if key in result:
                return str(result[key])
        try:
            return f"```json\n{json.dumps(result, indent=2, default=str)}\n```"
        except:
            return str(result)

    try:
        return str(result)
    except:
        return "Unable to display response."


# ---------- Chat card (history) ----------
with st.container():
    st.markdown('<div class="chat-card">', unsafe_allow_html=True)

    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Chat input + orchestrator call ----------
user_input = st.chat_input("Type your question or answer here...")

if user_input:
    # Add user message
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call orchestrator using InMemoryRunner (with session context)
    with st.spinner("Skillix is thinking..."):
        try:
            raw_result = runner.run_debug(
                user_input,
                session_id=SESSION_ID,
                user_id=USER_ID
            )
            bot_reply = extract_text_from_result(raw_result)
            if not bot_reply.strip():
                bot_reply = "I'm ready! How can I help you learn today?"
        except Exception as e:
            bot_reply = f"Error: {e}"

    # Show assistant reply
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    # Store in history
    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})


# ---------- Footer Hint ----------
st.markdown(
    '<div class="input-hint">Skillix is powered by Google ADK.</div>',
    unsafe_allow_html=True,
)