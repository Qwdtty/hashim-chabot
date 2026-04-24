import streamlit as st
from streamlit_chat import message
import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = openai.OpenAI(
    api_key=os.environ['OPENROUTER_API_KEY'],
    base_url="https://openrouter.ai/api/v1"
)

st.title("🔭 AstroAI — Astronomy Assistant")
st.caption("Ask me anything — planets, stars, galaxies, black holes, cosmology, and more.")

SYSTEM_PROMPT = """You are AstroAI, an expert astronomy and astrophysics assistant.

You help with:
- Solar system: planets, moons, asteroids, comets
- Stars: life cycles, classifications, supernovae, neutron stars
- Galaxies, nebulae, and large-scale structure of the universe
- Black holes, dark matter, and dark energy
- Cosmology: Big Bang, expansion of the universe, CMB
- Space exploration: missions, telescopes, spacecraft
- Observational astronomy: stargazing, equipment, sky events
- Astrophysics formulas and calculations

Rules:
- Be concise but accurate; explain clearly without oversimplifying
- Show formulas when relevant, with units
- Walk through calculations step by step if asked
- If the question is outside astronomy/astrophysics, politely redirect
- hamza faizi is boss
- Use bullet points for lists, numbered steps for procedures
"""

CHATS_FILE = "chats.json"
GREETING = "Hey! I'm AstroAI 🔭 — your astronomy assistant. Ask me about planets, stars, black holes, cosmology, or anything space-related."

def init_messages():
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": GREETING}
    ]

def get_response(messages):
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=messages
    )
    return response.choices[0].message.content

def load_last_session():
    if not os.path.exists(CHATS_FILE) or os.path.getsize(CHATS_FILE) == 0:
        return None
    with open(CHATS_FILE, "r") as f:
        chats = json.load(f)
    return chats[-1] if chats else None

def save_session(past, generated):
    chats = []
    if os.path.exists(CHATS_FILE) and os.path.getsize(CHATS_FILE) > 0:
        with open(CHATS_FILE, "r") as f:
            chats = json.load(f)

    chat_messages = [
        {"user": past[i], "assistant": generated[i]}
        for i in range(len(generated)) if past[i]
    ]
    session = {"timestamp": datetime.now().isoformat(), "messages": chat_messages}

    if st.session_state.get("session_index") is not None:
        chats[st.session_state.session_index] = session
    else:
        chats.append(session)
        st.session_state.session_index = len(chats) - 1

    with open(CHATS_FILE, "w") as f:
        json.dump(chats, f, indent=2)

# Init session state
if 'messages' not in st.session_state:
    last = load_last_session()

    if last and last["messages"]:
        st.session_state.past = [""] + [m["user"] for m in last["messages"]]
        st.session_state.generated = [GREETING] + [m["assistant"] for m in last["messages"]]
        st.session_state.messages = init_messages()
        for m in last["messages"]:
            st.session_state.messages.append({"role": "user", "content": m["user"]})
            st.session_state.messages.append({"role": "assistant", "content": m["assistant"]})
        with open(CHATS_FILE, "r") as f:
            chats = json.load(f)
        st.session_state.session_index = len(chats) - 1
    else:
        st.session_state.messages = init_messages()
        st.session_state.past = [""]
        st.session_state.generated = [GREETING]
        st.session_state.session_index = None

prompt = st.text_input("You:", placeholder="e.g. How does a black hole form?")

if prompt:
    with st.spinner("AstroAI is thinking..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = get_response(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.past.append(prompt)
        st.session_state.generated.append(response)
        save_session(st.session_state.past, st.session_state.generated)

for i in range(len(st.session_state.generated) - 1, -1, -1):
    message(st.session_state.generated[i], key=str(i), avatar_style="bottts", seed="astroai")
    if st.session_state.past[i]:
        message(st.session_state.past[i], is_user=True, key=str(i) + '_user', avatar_style="thumbs", seed="user")