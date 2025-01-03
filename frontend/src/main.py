import os
import requests
from PIL import Image
from functools import partial


import streamlit as st


# MATERIAL SYMBOLS
# https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded


from src.interface import Colors, cprint, center_text, hide_markdown_header_links, column_fix, fix_mobile_columns
from src.config import (
    APP_NAME,
    LANGSERVE_ENDPOINT,
    PORT,
    PIPELINE_ENDPOINT,
    STATIC_PATH
)

AVATAR_HUMAN = f"{STATIC_PATH}/user2.png"
AVATAR_AI = f"{STATIC_PATH}/assistant.png"

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content




def main_page():
    ip_addr = st.context.headers.get('X-Forwarded-For', "?")
    user_agent = st.context.headers.get('User-Agent', "?")
    lang = st.context.headers.get('Accept-Language', "?")
    cprint(f"RUNNING for: {ip_addr} - {lang} - {user_agent}", Colors.YELLOW)


    #### PAGE SETUP
    favicon = Image.open(os.path.join(STATIC_PATH, "favicon.ico"))
    st.set_page_config(
        # page_title="DEBUG!" if os.getenv("DEBUG", False) else "NOS4A2",
        page_title=APP_NAME,
        page_icon=favicon,
        layout="wide",
        # initial_sidebar_state="auto",
        initial_sidebar_state="collapsed",
    )


    #### BANNER
    center_text("p", "🗣️🤖💬", size=60)
    # st.header("🗣️🤖💬", divider="rainbow")
    # st.header("🗣️🤖💬")
    # hide_markdown_header_links()

    with st.popover("", icon=":material/settings:"):
        st.write(":orange[Settings]")


####################################################################################################################################



    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What do you want to learn?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # with st.spinner("Thinking..."):
        with st.chat_message("assistant"):
            response = requests.post(
                url=f"{LANGSERVE_ENDPOINT}:{PORT}{PIPELINE_ENDPOINT}",
                json={
                    "user_message": prompt,
                    "messages": st.session_state.messages,
                    "body": {},
                },
                stream=True,
            )
            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("Thinking..."):
                for chunk in response.iter_lines():
                    if chunk:
                        chunk_str = chunk.decode()
                        full_response += chunk_str
                        message_placeholder.markdown(full_response + "▌")
                        # message_placeholder.markdown(full_response)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})



####################################################################################################################################
    if os.getenv("DEBUG"):
        with st.sidebar.popover("DEBUG"):
            st.write(":orange[DEBUG]")
            st.write(st.secrets)
            st.write(st.session_state)
            st.write(st.context.cookies)
            st.write(st.context.headers)
