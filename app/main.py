import json
import os
import sys

from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from agents.agents import root_orchestrator
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
import asyncio

load_dotenv()

APP_NAME = "Skillix AI"
USER_ID = "student_01"
SESSION_ID = "session_01"

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

@st.cache_resource
def get_adk_runner():
    # This function will only run once per session
    return Runner(
        app_name=APP_NAME,
        agent=root_orchestrator,
        session_service=session_service,
        memory_service=memory_service
    )

runner = get_adk_runner()
# runner = Runner(
#     app_name=APP_NAME,
#     agent=root_orchestrator,
#     session_service=session_service,
#     memory_service=memory_service
# )

# Set page title and layout
st.set_page_config(page_title="Skillix AI", layout="centered")
st.title("🤖 Learn better with Skillix AI")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your tutor. Let's start learning by mentioning topic and your expertise level in that topic!"}
    ]

#extract result from the chat
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

async def agent_response(user_message: str) -> str:
    try:
        response = await runner.run_debug(
            user_message,  
            session_id=SESSION_ID,
            user_id=USER_ID
        )

        return extract_text_from_result(response)
    except Exception as e:
        response = f"Error during agent run: {str(e)}"
    
    return response

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#loop for the chat - interactive chat interface
async def chat_loop():
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = await agent_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

asyncio.run(chat_loop())
