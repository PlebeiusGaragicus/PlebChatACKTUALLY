import os
import enum
import requests
from PIL import Image
from functools import partial


import streamlit as st


# MATERIAL SYMBOLS
# https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded


from src.interface import Colors, cprint, center_text, hide_markdown_header_links, mobile_column_fix
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


def format_agents(arg):
    if arg == AgentEndpoints.phi.value:
        return "✨ :red[Phi-4]"

    elif arg == AgentEndpoints.llama.value:
        return "🦙 :green[Llama 3]"


def new_thread():
    st.session_state.messages = []



class AgentEndpoints(enum.Enum):
    phi = "phi"
    llama = "llama"



def cmp_options():
    # with st.popover("", icon=":material/menu:"):
    icon_color = "orange"
    icon = f":{icon_color}[:material/smart_toy:]"

    # with st.popover("", icon=icon):
    with st.popover(icon):
        st.markdown("### :grey[:material/settings:] :rainbow[Settings]")

        # TODO doesn't work
        # if len(st.session_state.get("messages", [])) > 0:
        #     if st.button(":red[Clear conversation]"):
        #         st.rerun()

        # with st.container(height=300, border=False):
        with st.container(border=False):
            st.radio(
                ":blue[Choose your Agent]",
                (AgentEndpoints.phi.value, AgentEndpoints.llama.value),
                horizontal=True,
                index=0,
                key="model",
                format_func=format_agents,
                on_change=new_thread,
            )

            st.radio(
                ":blue[Choose your Voice]",
                ("👤 Human", "🤖 AI"),
                horizontal=True,
                index=0,
                key="voice",
            )

            # st.radio(
            #     ":blue[Something else]",
            #     ("blah blah", "another thing"),
            #     horizontal=True,
            #     index=0,
            # )

            # st.radio(
            #     ":blue[So many options!]",
            #     ("blah blah", "another thing"),
            #     horizontal=True,
            #     index=0,
            # )

            # st.radio(
            #     ":blue[Too many options?]",
            #     ("blah blah", "another thing", "yes", "no", "maybe"),
            #     horizontal=True,
            #     index=0,
            # )


def cmp_header():

    # header_text = "🗣️🤖💬"
    # if st.session_state.model == AgentEndpoints.phi.value:
    #     header_text += " :material/router:"
    # elif st.session_state.model == AgentEndpoints.llama.value:
    #     header_text += " 🦙"

    # center_text("p", header_text, size=40)
    # st.header(header_text, divider="rainbow")
    # st.header("🗣️🤖💬", divider="rainbow")
    # st.header("🗣️🤖💬")

    st.header(":rainbow[PlebChat :] " + format_agents(st.session_state.model), divider="rainbow")


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

    header_placeholder = st.empty()

    cmp_options()

    with header_placeholder:
        cmp_header()

    hide_markdown_header_links()




####################################################################################################################################



    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=AVATAR_HUMAN if message["role"] == "user" else AVATAR_AI):
            st.markdown(message["content"])

    if prompt := st.chat_input("What do you want to learn?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_HUMAN):
            st.markdown(prompt)

        # with st.spinner("Thinking..."):
        with st.chat_message("assistant", avatar=AVATAR_AI):
            response = requests.post(
                url=f"{LANGSERVE_ENDPOINT}:{PORT}/{st.session_state.model}",
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
                for line in response.iter_lines():
                    if line:
                        line = line.decode()
                        print("Received:", line)
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix
                            # Decode escaped newlines
                            chunk = chunk.replace('\\n', '\n')
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})



####################################################################################################################################
    # if os.getenv("DEBUG"):
    #     with st.sidebar.popover("DEBUG"):
    #         st.write(":orange[DEBUG]")
    #         st.write(st.secrets)
    #         st.write(st.session_state)
    #         st.write(st.context.cookies)
    #         st.write(st.context.headers)
