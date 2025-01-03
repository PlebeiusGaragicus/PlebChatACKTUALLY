import streamlit as st
import requests
import json
import os

from src.common import (
    not_init,
    is_init
)

from src.config import (
    APP_NAME, LANGSERVE_ENDPOINT,
    PORT, PIPELINE_ENDPOINT,
    STATIC_PATH
)

from src.components.buttons import cmp_buttons


# STATIC_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")


def interrupt():
    """Callback for the interrupt button"""
    if 'incomplete_stream' in st.session_state:
        st.session_state.thread['messages'].append({
            'role': 'assistant',
            'content': st.session_state.incomplete_stream
        })
        st.session_state.thread['messages'].append({
            'role': 'user',
            'content': "<INTERRUPTS>"
        })


def cmp_chat_window():
    # Use static avatars
    human_avatar = f"{STATIC_PATH}/user2.png"
    ai_avatar = f"{STATIC_PATH}/assistant.png"

    st.chat_message("assistant", avatar=ai_avatar).write("Hello! How can I help you today?")

    if is_init("thread"):
        for message in st.session_state.thread['messages']:
            with st.chat_message(message['role'], avatar=ai_avatar if message['role'] == "assistant" else human_avatar):
                st.markdown(message['content'])

    prompt = st.chat_input("Message (⌘-Enter to submit)")
    
    if prompt:
        # Add user message
        if not is_init("thread"):
            st.session_state.thread = {'messages': []}
            
        st.session_state.thread['messages'].append({
            'role': 'user',
            'content': prompt
        })
        
        # Display user message
        with st.chat_message("user", avatar=human_avatar):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant", avatar=ai_avatar):
            response_placeholder = st.empty()
            
            try:
                # Make API request
                response = requests.post(
                    f"{LANGSERVE_ENDPOINT}:{PORT}/{PIPELINE_ENDPOINT}",
                    json={"input": {"messages": st.session_state.thread['messages']}}
                )
                
                if response.status_code == 200:
                    assistant_response = response.json()['output']
                    response_placeholder.markdown(assistant_response)
                    
                    # Add assistant response to thread
                    st.session_state.thread['messages'].append({
                        'role': 'assistant',
                        'content': assistant_response
                    })
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    response_placeholder.error(error_msg)
                    st.session_state.thread['messages'].append({
                        'role': 'assistant',
                        'content': error_msg
                    })
            
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                response_placeholder.error(error_msg)
                st.session_state.thread['messages'].append({
                    'role': 'assistant',
                    'content': error_msg
                })

    # Display buttons
    # with new_button_placeholder:
        # cmp_buttons()
    cmp_buttons()
