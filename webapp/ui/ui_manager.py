"""Utility functions for handling displaying of different widgets on UI
"""
import os
import base64
import webvtt
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from ui.chatbot import Chatbot
from common import time_to_seconds, load_course_material
from config import DATASET_COURSE_BASE_DIR

from utils.logging_handler import Logger
from moviepy.editor import VideoFileClip


# load the course material
course_material = load_course_material(DATASET_COURSE_BASE_DIR)
courses = course_material["course_names"]
course_logos = [course_material[course]["logo_path"] for course in courses]


def display_video(video_path: Path, start_time: int = 0, add_style=True, width=500, height=400):
    """Displays a video player with the given width and height if add_style is True (default)

    Args:
        video_path (Path): _description_
        add_style (bool, optional): _description_. Defaults to True.
        width (int, optional): _description_. Defaults to 200.
        height (int, optional): _description_. Defaults to 100.
    """
    if add_style:
        # Set the CSS style to adjust the size of the video
        thumbnail_style = f"""
            video {{
                width: {width}px !important;
                height: {height}px !important;
            }}
        """
        st.markdown(f'<style>{thumbnail_style}</style>',
                    unsafe_allow_html=True)
    st.video(str(video_path), start_time=start_time)


def set_chat_window_style():
    """Customizes the style of the chat window
    """
    css = """
    <style>
    .chat_container {
        background-color: #F2F2F2;
        padding: 1px;
        border-radius: 5px;
        height: 20px;
        overflow-y: auto;
    }
    </style>
    """
    components.html(css, height=0)


def set_session_state(state_name, state_value):
    st.session_state[state_name] = state_value


def display_course_banner(course_name):
    """Displays a course banner for the given course.

    Args:
        course_name (_type_): _description_
    """
    course_index = courses.index(course_name)
    image_style = """
        img {
            # width: 1000px !important;
            height: 200px !important;
        }
    """
    st.markdown(f'<style>{image_style}</style>', unsafe_allow_html=True)
    st.image(str(course_logos[course_index]), use_column_width=True)


def display_courses():
    """Creates a display for courses arranged in 2 columns.
    """
    image_style = """
        img {
            width: 200px !important;
            height: 100px !important;
        }
    """
    # st.markdown(f'<style>{image_style}</style>', unsafe_allow_html=True)
    for i in range(0, len(course_logos), 2):
        col_1, col_2 = st.columns([1, 1])
        with col_1:
            with st.container():
                st.image(str(course_logos[i]), use_column_width=True)
                st.button(label=courses[i], use_container_width=True, on_click=set_session_state, kwargs={
                          "state_name": "course_selected", "state_value": courses[i]})
        with col_2:
            if i+1 < len(course_logos):
                with st.container():
                    st.image(str(course_logos[i+1]), use_column_width=True)
                    st.button(label=courses[i+1], use_container_width=True, on_click=set_session_state, kwargs={
                              "state_name": "course_selected", "state_value": courses[i+1]})


def display_video_content(video_file: Path):
    """Displays the video on the UI along with its subtitle on right side

    Args:
        video_file (Path): _description_
    """
    Logger.info("Selected video: {}".format(str(video_file)))
    # Create two columns with a width ratio of 2:1
    video_panel, text_panel = st.columns([1.5, 1])

    # Content for the left column
    with video_panel:
        # st.header("Video Lectures")
        display_video(video_path=video_file, add_style=False)

    # Content for the right column
    with text_panel:
        doc_file = os.path.join(
            "/".join(str(video_file).split("/")[:-1]), "subtitle-en.vtt")
        subtitles = webvtt.read(doc_file)
        transcript = ""
        for subtitle in subtitles:
            start, end = subtitle.start, subtitle.end
            subtitle_text = " ".join(subtitle.text.strip().split("\n")).strip()
            transcript += "{} --> {}\n{}\n\n".format(start, end, subtitle_text)

        st.text_area(label="Video Transcript:",
                     value=transcript, height=280)

    st.markdown("---")


def display_qa_chat_bot():
    """Displays a chat-bot on UI for QA
    """
    # display_chat()
    chatbot = Chatbot(callback=callback_video_player, video_path=Path(
        st.session_state['video_selected']))
    chatbot.listen_for_inputs()


def generate_video_clip(video_path: Path, start_time: int, end_time: int, output_path: Path) -> Path:
    """Generates a video clip from the given video file and stores it in output_path

    Args:
        video_path (Path): path to video file
        start_time (int): start time
        end_time (int): end time
        output_path (Path): path to clip to be stored

    Returns:
        Path: _description_
    """
    video_clip = VideoFileClip(str(video_path))
    video_clip = video_clip.subclip(start_time, end_time)
    video_clip.write_videofile(str(output_path))
    return output_path


def callback_video_player(meta_data, video_path: Path):
    """Display a video player for the video_path and set the start time to time available in the meta_data.
    Also generates a video clip from the video_path
    Args:
        meta_data (_type_): contains a key "start_timestamp" for the start time value in format "%H:%M:%S.%f"
        video_path (Path): path to video to be displayed
    """
    start_time = time_to_seconds(time_string=meta_data["start_timestamp"])
    print(f'Video: {video_path}\nstart time: {start_time}')

    display_video(video_path=video_path, start_time=start_time)

    video_clip_dir = video_path.parent / 'short_clips'
    video_clip_dir.mkdir(parents=True, exist_ok=True)
    video_clip_path = video_clip_dir / \
        f'{video_path.stem}_clip_{start_time}.mp4'
    video_clip_path = generate_video_clip(video_path=video_path, start_time=start_time,
                                end_time=start_time+30, output_path=video_clip_path)
    
    # display_video(video_path=video_clip_path)


def display_viva_chat_bot(selected_course):
    """Displays a chat-bot on UI for taking VIVA
    """
    # display_chat()
    chatbot = Chatbot(chat_box_label="", viva_mode=True,
                      selected_course=selected_course)
    chatbot.listen_for_inputs()


def display_video_clips(selected_course):
    """Creates a UI for selecting videos for the selected course. Videos are arranged in 3 columns.
    All videos from the config path is displayed.
    """
    study_material = course_material[selected_course]["Study-Material"]
    week_names = study_material["week_names"]

    week_tabs = st.tabs(week_names)
    for week_name, week_tab in zip(week_names, week_tabs):
        with week_tab:
            subtopic_names = study_material[week_name]["subtopic_names"]
            course_video_clips = []
            for subtopic in subtopic_names:
                video_clips = study_material[week_name][subtopic].get(
                        "video_clips", [])
                course_video_clips.extend(video_clips)
            print(course_video_clips)
            if not course_video_clips:
                return
            current_selected_clip_index = 0
            if "video_clip_selected_index" not in st.session_state:
                st.session_state["video_clip_selected_index"] = 0
            else:
                current_selected_clip_index = st.session_state["video_clip_selected_index"]
            
            no_of_clips = len(course_video_clips)
            # for video_clip in course_video_clips:
            #     with st.container():
            #         display_video(video_path=video_clip, add_style=True)
            col_1, col_2 = st.columns([1, 1])

            for i in range(0, len(course_video_clips), 2):

                with col_1:
                    video_path = course_video_clips[i]
                    # subtopic_name = subtopic_names[i]
                    if video_path is not None:
                        with st.container():
                            display_video(video_path=video_path,
                                          add_style=False)
                            st.button(label=video_path, key=f"{week_tab}{i}", use_container_width=True, on_click=set_session_state, kwargs={
                                "state_name": "video_selected", "state_value": video_path})

                with col_2:
                    if i+1 < len(course_video_clips):
                        video_path = course_video_clips[i+1]
                        # subtopic_name = subtopic_names[i+1]
                        if video_path is not None:
                            with st.container():
                                display_video(
                                    video_path=video_path, add_style=False)
                                st.button(label=video_path, key=f"{week_tab}{i+1}", use_container_width=True, on_click=set_session_state, kwargs={
                                    "state_name": "video_selected", "state_value": video_path})
            # with st.container():
            #     display_video(video_path=course_video_clips[current_selected_clip_index], add_style=True)
            # next_selected_clip_index = (current_selected_clip_index + 1) % no_of_clips
            # print(next_selected_clip_index)
            # st.button(label='Next', key=f"{week_tab}", use_container_width=True, on_click=set_session_state, kwargs={
            #     "state_name": "video_clip_selected_index", "state_value": next_selected_clip_index})
            

def display_video_tabs(selected_course):
    """Creates a UI for selecting videos for the selected course. Videos are arranged in 3 columns.
    All videos from the config path is displayed.
    """
    study_material = course_material[selected_course]["Study-Material"]
    week_names = study_material["week_names"]

    week_tabs = st.tabs(week_names)
    for week_name, week_tab in zip(week_names, week_tabs):
        with week_tab:
            subtopic_names = study_material[week_name]["subtopic_names"]
            col_1, col_2 = st.columns([1, 1])

            for i in range(0, len(subtopic_names), 2):

                with col_1:
                    video_path = study_material[week_name][subtopic_names[i]].get(
                        "video_file", None)
                    subtopic_name = subtopic_names[i]
                    if video_path is not None:
                        with st.container():
                            display_video(video_path=video_path,
                                          add_style=False)
                            st.button(label=subtopic_name, key=f"{week_tab}{i}", use_container_width=True, on_click=set_session_state, kwargs={
                                "state_name": "video_selected", "state_value": video_path})

                with col_2:
                    if i+1 < len(subtopic_names):
                        video_path = study_material[week_name][subtopic_names[i+1]].get(
                            "video_file", None)
                        subtopic_name = subtopic_names[i+1]
                        if video_path is not None:
                            with st.container():
                                display_video(
                                    video_path=video_path, add_style=False)
                                st.button(label=subtopic_name, key=f"{week_tab}{i+1}", use_container_width=True, on_click=set_session_state, kwargs={
                                    "state_name": "video_selected", "state_value": video_path})

    st.markdown("---")
    st.button(label="Take a Revision", use_container_width=True, on_click=set_session_state, kwargs={
              "state_name": "revision_mode",
              "state_value": True
              })
    st.button(label="Course Viva Exam", use_container_width=True, on_click=set_session_state, kwargs={
              "state_name": "viva_mode",
              "state_value": True
              })
