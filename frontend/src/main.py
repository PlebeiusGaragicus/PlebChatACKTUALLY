import os
import requests
import streamlit as st
import json
from typing import List, Dict, Optional

from src.common import cprint, Colors
from src.config import APP_NAME
from src.components.chat_window import cmp_chat_window
from src.components.cmp_header import cmp_header


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

    # Main chat interface
    cmp_header(APP_NAME)

    # Display the chat interface
    cmp_chat_window()

    cmp_debug()