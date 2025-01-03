import os
import requests
import streamlit as st

from src.common import cprint, Colors
from src.interface import cmp_header, center_text

APP_NAME = "Template"


def log_rerun():
    ip_addr = st.context.headers.get('X-Forwarded-For', "?")
    user_agent = st.context.headers.get('User-Agent', "?")
    lang = st.context.headers.get('Accept-Language', "?")

    # print(f"RUNNING for IP address: {ip_addr}")
    cprint(f"RUNNING for: {ip_addr} - {lang} - {user_agent}", Colors.YELLOW)


def cmp_debug():
    if os.getenv("DEBUG"):
        with st.sidebar.popover("DEBUG"):
            st.write(":orange[DEBUG]")
            st.write(st.secrets)
            st.write(st.session_state)
            st.write(st.context.cookies)
            st.write(st.context.headers)


def main_page():
    log_rerun()

    cmp_header(APP_NAME)

    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever
    st.header("", divider="rainbow")



    st.write("## Ask a question")
    prompt = st.text_area(
        "Prompt",
        value="",
        key="prompt"
    )
    if st.button("Ask a question"):
        # make a request to the API
        response = requests.post(
            "http://backend:8000/chat",
            json={
                "message": prompt
            }
        )
        st.write(response.json())
