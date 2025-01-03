import os
import pathlib
from PIL import Image

import streamlit as st

from src.config import STATIC_PATH


# BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
# from enum import Enum, auto
# class Colors(Enum):
class Colors():
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

def colorize(color: int):
    return f'\033[1;3{color}m'

def cprint(string: str, color: Colors):
    print_this = f'\033[1;3{color}m' + string + '\033[0m'

    if os.getenv("DEBUG", True):
        print(print_this)
    else:
        pass



def center_text(type, text, size=None):
    if size == None:
        st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)
    else:
        st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)



# # https://github.com/streamlit/streamlit/issues/5003
# def column_fix():
#     # TODO: what does this to again...? A fix for mobile?
# #     st.write("""<style>
# # [data-testid="column"] {
# #     width: calc(33.3333% - 1rem) !important;
# #     flex: 1 1 calc(33.3333% - 1rem) !important;
# #     min-width: calc(33% - 1rem) !important;
# # }
# # </style>""", unsafe_allow_html=True)

# # def fix_mobile_columns():    
#     st.write('''<style>
#     [data-testid="column"] {
#         width: calc(16.6666% - 1rem) !important;
#         flex: 1 1 calc(16.6666% - 1rem) !important;
#         min-width: calc(16.6666% - 1rem) !important;
#     }
#     </style>''', unsafe_allow_html=True)

def column_fix():
    st.write('''<style>
[data-testid="column"] {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>''', unsafe_allow_html=True)

def fix_mobile_columns():    
    st.write('''<style>
    [data-testid="column"] {
        width: calc(16.6666% - 1rem) !important;
        flex: 1 1 calc(16.6666% - 1rem) !important;
        min-width: calc(16.6666% - 1rem) !important;
    }
    </style>''', unsafe_allow_html=True)



def centered_button_trick():
    """ Use this in a `with` statement to center a button.
    
    Example:
    ```python
    with centered_button_trick():
        st.button(
            "👈 back",
            on_click=go_to_main_page,
            use_container_width=True)
    ```
    """
    columns = st.columns((1, 2, 1))
    with columns[0]:
        st.empty()
    # with columns[1]:
        # normally the button logic would go here
    with columns[2]:
        st.empty()

    return columns[1]



# def hide_anchor_link():
def hide_markdown_header_links():
    """
    https://discuss.streamlit.io/t/hide-titles-link/19783/3
    """

        # <style>
        # .css-15zrgzn {display: none}
        # .css-eczf16 {display: none}
        # .css-jn99sy {display: none}
        # .st-emotion-cache-gi0tri {display: none}
        # .e121c1cl3 {display: none}
        # </style>
    st.markdown("""
        <style>
        .stApp a:first-child {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)

