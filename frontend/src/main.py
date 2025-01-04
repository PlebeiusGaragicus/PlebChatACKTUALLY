import os
import enum
import requests
from PIL import Image
from functools import partial

import streamlit as st


# MATERIAL SYMBOLS
# https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded



## TODO: get markdown to show local images
# https://discuss.streamlit.io/t/local-image-button/5409/6



from src.config import APP_NAME, LANGSERVE_ENDPOINT, PORT, STATIC_PATH
from src.interface import Colors, cprint, center_text, hide_markdown_header_links, hide_stop_button, mobile_column_fix
from src.login import login

AVATAR_HUMAN = f"{STATIC_PATH}/user2.png"
AVATAR_AI = f"{STATIC_PATH}/assistant.png"

class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content




class AgentEndpoints(enum.Enum):
    phi = "phi"
    llama = "llama"
    research = "research"



def format_agents(arg):
    if arg == AgentEndpoints.phi.value:
        return "✨:red[Phi-4]"

    elif arg == AgentEndpoints.llama.value:
        return "🦙:green[Llama 3]"

    elif arg == AgentEndpoints.research.value:
        return "🌐:violet[Researcher]"


def new_thread():
    st.session_state.messages = []





################################################################################################
def cmp_options():
    # with st.popover("", icon=":material/menu:"):
    icon_color = "orange"
    # icon = f":{icon_color}[:material/smart_toy:]"
    icon = f":{icon_color}[:material/smart_toy:] :rainbow[PlebChat]"

    # with st.popover("", icon=icon):
    with st.popover(icon):
        # st.markdown("### :grey[:material/settings:] :rainbow[Intellence Settings]")
        # st.markdown("### :grey[:material/settings:] :rainbow[Intelligent Agents]")

        # with st.container(height=200, border=False):
        # with st.container(height=150):
        # with st.container(border=False):
        # st.markdown("### :grey[Select Agent]")
        st.radio(
            # ":blue[Choose your Agent]",
            "",
            (AgentEndpoints.phi.value, AgentEndpoints.llama.value, AgentEndpoints.research.value),
            horizontal=True,
            index=0,
            key="model",
            format_func=format_agents,
            on_change=new_thread,
        )

        if st.session_state.model == AgentEndpoints.phi.value:
            # with st.container(height=200, border=True):
            # with st.expander(":grey[Configure Agent]", icon=":material/settings:", expanded=False):
            with st.expander(":grey[:material/settings: Configure Agent]", expanded=False):
                st.radio(
                    ":blue[Choose your Voice]",
                    ("👤 Human", "🤖 AI"),
                    horizontal=True,
                    index=0,
                    key="voice",
                )
                st.text_input(":blue[Your Name]", key="name", value="Pleb")
        else:
            st.session_state.voice = None



        st.divider()
        # bcols2 = st.columns([1, 1], gap="small")
        # with bcols2[0]:
        #     if st.button(":green[Done]", on_click=new_thread):
        #         pass
        # with bcols2[1]:
        #     st.session_state.authenticator.logout(":red[Logout]")
        st.session_state.authenticator.logout(":red[Logout]")

################################################################################################
# END OF SETTINGS POPUP
################################################################################################





################################################################################################
def main_page():
    if os.getenv("DEBUG", False): # should be the only time we call this
        st.session_state.debug = True
    else:
        st.session_state.debug = False

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
        # initial_sidebar_state="collapsed",
    )

    if not login():
        st.stop()


    header_placeholder = st.empty()
    cmp_options()
    with header_placeholder:
        # cmp_header()
        # st.header(":rainbow[PlebChat :] " + format_agents(st.session_state.model), divider="rainbow")
        st.header("" + format_agents(st.session_state.model), divider="rainbow")


    mobile_column_fix()
    hide_markdown_header_links()
    if not st.session_state.debug:
        hide_stop_button()




####################################################################################################################################
    if "messages" not in st.session_state:
        st.session_state.messages = []

        ## FIRST RUN TOAST BANNER
        # st.toast(":rainbow[Welcome to PlebChat!]", icon=":material/smart_toy:")
        # st.toast("#### :rainbow[Welcome to PlebChat!]")



    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=AVATAR_HUMAN if message["role"] == "user" else AVATAR_AI):
            st.markdown(message["content"])

    if prompt := st.chat_input(placeholder="What do you want to learn?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_HUMAN):
            st.markdown(prompt)


        with st.chat_message("assistant", avatar=AVATAR_AI):
            response = requests.post(
                url=f"{LANGSERVE_ENDPOINT}:{PORT}/{st.session_state.model}",
                json={
                    "user_message": prompt,
                    "messages": st.session_state.messages,
                    "body": {}, #TODO user_id
                },
                stream=True,
            )
            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("🧠 Thinking..."):
                for line in response.iter_lines():
                    if line:
                        line = line.decode()
                        # print("Received:", line)
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix
                            # Decode escaped newlines
                            chunk = chunk.replace('\\n', '\n')
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})



####################################################################################################################################
    if st.session_state.debug:
        with st.sidebar:
            st.write(st.secrets)
            st.write(st.session_state)
            st.write(st.context.cookies)
            st.write(st.context.headers)
