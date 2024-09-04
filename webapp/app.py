import streamlit as st

from PIL import Image
from pathlib import Path
from config import BASE_DIR
from ui.ui_manager import *

from utils.logging_handler import Logger

def write_header():
    """Writes the header part of the UI
    """
    # st.markdown("---")
    st.title(':blue[LEAP (Learning Enhancement and Assistance Platform)]')
    # st.markdown('''
    #     - Intel One API hackathon implementation of LEAP platform
    # ''')


def write_footer():
    """Writes the footer part of the UI
    """
    st.sidebar.markdown("---")
    st.sidebar.warning("Please note that this tool is only for demo purpose")
    st.sidebar.text('''
       © Copyright 2023, Course5 AI Labs.
    ''')


def write_ui():
    """Handles the major part of the UI
    """

    # Sets up the basic UI with title and logo
    st.sidebar.title("Course5 AI Labs")
    img = Image.open(Path(BASE_DIR) / 'imgs/c5-logo.jpeg')
    st.sidebar.image(img)

    if "demo_started" not in st.session_state:
        # Handles the initial page which displays the process flow
        st.session_state["demo_started"] = False
        img = Image.open(Path(BASE_DIR) / 'imgs/process-flow.png')
        st.image(img, use_column_width=True)
        if st.button(label="Start Demo", use_container_width=True):
            st.session_state["demo_started"] = True
    elif "revision_mode" in st.session_state:
        display_course_banner(st.session_state["course_selected"])
        st.markdown("---")
        display_video_clips(st.session_state["course_selected"])
    elif "viva_mode" in st.session_state:
        display_course_banner(st.session_state["course_selected"])
        st.markdown("---")
        display_viva_chat_bot(st.session_state["course_selected"])
    elif "course_selected" not in st.session_state:
        # Handles the page to display the course selection page
        st.markdown("---")
        display_courses()
    elif "video_selected" not in st.session_state:
        # Handles the page to display course contents from which a video can be selected
        display_course_banner(st.session_state["course_selected"])
        display_video_tabs(st.session_state["course_selected"])
    else:
        # Handles the UI to have Q&A on selected video
        st.markdown("---")
        video_selected = st.session_state["video_selected"]
        # Display video and subtitles on UI
        display_video_content(Path(video_selected))
        # Chat window
        display_qa_chat_bot()


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (st.session_state["username"] in st.secrets["passwords"]
                and st.session_state["password"]
                == st.secrets["passwords"][st.session_state["username"]]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password",
                      type="password",
                      on_change=password_entered,
                      key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password",
                      type="password",
                      on_change=password_entered,
                      key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

def production_mode():
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    a[class^="viewerBadge_container*"]  {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    return

if __name__ == '__main__':
    img = Image.open(Path(BASE_DIR) / 'imgs/c5-favicon.jpeg')
    st.set_page_config(page_title='LEAP',
                       page_icon=img,
                       layout='wide')

    #if check_password():
    #production_mode()
    write_header()
    write_ui()
    write_footer()
