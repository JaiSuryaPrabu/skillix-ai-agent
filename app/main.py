# main.py

import json
import streamlit as st
from agents.orchestrator import create_orchestrator_agent
from google.adk.runners import Runner
from google.genai import types


# --------- Orchestrator + Runner (created once) --------- #
@st.cache_resource
def get_runner() -> Runner:
    """
    Initialize the orchestrator agent and wrap it in an ADK Runner.
    This is created once per app session and reused.
    """
    orchestrator_agent = create_orchestrator_agent()
    return Runner(orchestrator_agent)


runner = get_runner()


# --------- Streamlit Page Setup --------- #
st.set_page_config(
    page_title="Skillix AI",
    page_icon="🤖",
    layout="centered",
)

# ---------- Custom CSS for nicer UI ----------
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
    # Each item: {"role": "user" | "assistant", "content": str}
    st.session_state["messages"] = []


# --------- Top Row: Info + Reset Button --------- #
col_info, col_reset = st.columns([4, 1])

with col_info:
    st.markdown(
        "💬 **Chat with Skillix** — ask questions, answer prompts, and get evaluated in real time."
    )

with col_reset:
    if st.button("🔁 Reset chat", use_container_width=True):
        st.session_state["messages"] = []
        st.experimental_rerun()


# --------- Helper: Extract text from Runner result --------- #
def extract_text_from_result(result) -> str:
    """
    Extracts a clean text string from the Runner output, handling native
    google.genai types, dictionaries, and plain strings.
    """

    # 1. Handle native google.genai types

    # a) Top-level GenerateContentResponse from google.genai
    if isinstance(result, types.GenerateContentResponse):
        # .text is a convenience property that aggregates text parts
        try:
            return result.text or ""
        except ValueError:
            # Fallback if the response was blocked or empty
            return "⚠️ No text content generated (possibly blocked)."

    # b) Content object (standard message container)
    if isinstance(result, types.Content):
        text_parts = []
        if getattr(result, "parts", None):
            for part in result.parts:
                if getattr(part, "text", None):
                    text_parts.append(part.text)
        return "".join(text_parts)

    # c) Single Part object
    if isinstance(result, types.Part):
        return getattr(result, "text", "") or ""

    # 2. Handle plain string directly
    if isinstance(result, str):
        return result

    # 3. Handle dict-based outputs (common in some ADK configurations)
    if isinstance(result, dict):
        # If output is wrapped in {"output": ...}
        if "output" in result:
            out = result["output"]
            if isinstance(out, dict):
                if "text" in out:
                    return str(out["text"])
                if "output_text" in out:
                    return str(out["output_text"])
            return str(out)

        # Direct keys in the dict
        for key in ("text", "output_text", "message"):
            if key in result:
                return str(result[key])

        # Fallback: pretty-print the dict as JSON
        try:
            return "```json\n" + json.dumps(result, indent=2, default=str) + "\n```"
        except Exception:
            return str(result)

    # 4. Final fallback
    try:
        return str(result)
    except Exception:
        return "⚠️ Unable to display response."


# ---------- Chat card (history) ----------
with st.container():
    st.markdown('<div class="chat-card">', unsafe_allow_html=True)

    # Show previous messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Chat input + orchestrator call ----------
user_input = st.chat_input("Type your question or answer here...")

if user_input:
    # 1) add user message to history and show it
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2) call orchestrator via Runner
    try:
        result = runner.run_debug(user_input)
        bot_reply = extract_text_from_result(result)
    except Exception as e:
        # fallback message if orchestrator fails
        bot_reply = f"⚠️ Error while calling orchestrator:\n\n`{e}`"

    # 3) show bot reply
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    # 4) store bot reply in history
    st.session_state["messages"].append(
        {"role": "assistant", "content": bot_reply}
    )

st.markdown(
    '<div class="input-hint">Skillix is powered by multi-agent orchestration.</div>',
    unsafe_allow_html=True,
)
