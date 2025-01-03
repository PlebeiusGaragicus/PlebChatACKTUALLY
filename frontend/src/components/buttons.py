import streamlit as st
from src.common import not_init


def new_thread():
    """Create a new chat thread by clearing the messages"""
    if 'thread' in st.session_state:
        del st.session_state.thread
    st.session_state.thread = {'messages': []}
    st.toast("Started new chat!", icon="🌱")


def cmp_buttons():
    """Display action buttons for thread management"""
    if not_init("thread"):
        return

    with st.container():
        if len(st.session_state.thread['messages']) > 0:
            # New Thread button
            # st.popover
            with st.popover("🌱 :green[New Chat]"):
                st.button(
                    "🌱 :green[New Chat]", 
                    on_click=new_thread, 
                    use_container_width=True,
                    key="btn_new_chat"
                )
