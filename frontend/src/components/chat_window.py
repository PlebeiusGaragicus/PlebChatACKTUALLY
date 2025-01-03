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


@st.fragment
def cmp_chat_window():
    # Use static avatars
    human_avatar = f"{STATIC_PATH}/user2.png"
    ai_avatar = f"{STATIC_PATH}/assistant.png"

    # UI Controls in columns
    cols = st.columns((1, 1, 1))
    with cols[0]:
        speech_input = st.toggle("🗣️🤖", key="speech_input", value=False)
    with cols[1]:
        read_to_me = st.toggle("🤖💬", key="read_to_me", value=False)

    # Welcome message for new chat
    # if not is_init("thread"):
    st.chat_message("assistant", avatar=ai_avatar).write("Hello! How can I help you today?")

    # Display chat history
    if is_init("thread"):
        for message in st.session_state.thread['messages']:
            with st.chat_message(message['role'], avatar=ai_avatar if message['role'] == "assistant" else human_avatar):
                st.markdown(message['content'])

    # Create placeholders for dynamic content
    user_message_placeholder = st.empty()
    cols2 = st.columns((1, 1))
    with cols2[0]:
        interrupt_button_placeholder = st.empty()
    response_placeholder = st.empty()

    # Chat input
    prompt = st.chat_input("Message (⌘-Enter to submit)")
    
    if prompt:
        # Initialize thread if needed
        if not is_init("thread"):
            st.session_state.thread = {'messages': []}

        # Add and display user message
        st.session_state.thread['messages'].append({
            'role': 'user',
            'content': prompt
        })
        
        user_message_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)

        # Display assistant response
        with response_placeholder.chat_message("assistant", avatar=ai_avatar):
            message_placeholder = st.empty()
            
            # Show interrupt button during response
            interrupt_button_placeholder.button(
                "🛑 Interrupt",
                on_click=interrupt,
                key="button_interrupt"
            )
            
            try:
                # Make API request
                response = requests.post(
                    f"{LANGSERVE_ENDPOINT}:{PORT}/{PIPELINE_ENDPOINT}",
                    json={"input": {"messages": st.session_state.thread['messages']}}
                )
                
                if response.status_code == 200:
                    assistant_response = response.json()['output']
                    message_placeholder.markdown(assistant_response)
                    
                    # Add assistant response to thread
                    st.session_state.thread['messages'].append({
                        'role': 'assistant',
                        'content': assistant_response
                    })

                    # Handle text-to-speech if enabled
                    if read_to_me:
                        st.session_state.speak_this = assistant_response
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    message_placeholder.error(error_msg)
                    st.session_state.thread['messages'].append({
                        'role': 'assistant',
                        'content': error_msg
                    })
            
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.thread['messages'].append({
                    'role': 'assistant',
                    'content': error_msg
                })

            # Clear interrupt button after response
            interrupt_button_placeholder.empty()

    # Display buttons at the bottom
    cmp_buttons()
