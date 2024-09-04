import os
from pathlib import Path
import streamlit as st
import speech_recognition as sr
from datetime import datetime
from speech_recognition import UnknownValueError

from utils.logging_handler import Logger

@st.cache_data
def convert_stt(audio_bytes):
    """Listens for any user input in chatbot UI. Inputs can be via text or via microphone.
    """
    recognized_text = None
    if audio_bytes:
        try:
            Logger.info("Running STT...")
            r = sr.Recognizer()
            audio_data = sr.AudioData(
                frame_data=audio_bytes, sample_rate=16000, sample_width=4)
            recognized_text = str(
                r.recognize_whisper(audio_data=audio_data))
            Logger.info(f"STT recognized text: {recognized_text}")
        except UnknownValueError as unrecognized_audio_error:
            Logger.exception(unrecognized_audio_error)

    return recognized_text

def get_viva_context(base_dir, topic_name):
    """Get the context for specific topic for Viva Exam
    """
    dir_path = os.path.join(base_dir, topic_name, "Viva-Material")
    context = ""
    for curr_path in os.listdir(dir_path):
        if ".txt" in curr_path:
            with open(os.path.join(dir_path, curr_path), "r", encoding='utf-8') as f:
                data = f.read()
            context += str(data)  + "\n\n"
    
    return context

def load_course_material(base_dir):
    """Load the course material
    """
    course_material = {"course_names": []}
    # courses/{topic_name}/{material_type}/{week_name}/{sub_topic_name}/
    for topic_name in sorted(os.listdir(base_dir)):
        curr_dir = os.path.join(base_dir, topic_name)
        if os.path.isdir(curr_dir) is False:
            continue
        course_material["course_names"].append(topic_name)
        if topic_name not in course_material:
            course_material[topic_name] = {}

        for _type in sorted(os.listdir(curr_dir)):
            _curr_dir = os.path.join(curr_dir, _type)

            if os.path.isfile(_curr_dir):
                if _type.split('.')[-1] in ["jpeg", "png", "jpg"]:
                    course_material[topic_name][
                        "logo_path"] =  os.path.join(curr_dir, _type)
                    continue

            if os.path.isdir(_curr_dir) is False:
                continue

            if _type == "Study-Material":
                course_material[topic_name][_type] = {"week_names": []}
                
                for week_name in sorted(os.listdir(_curr_dir)):
                    __curr_dir = os.path.join(_curr_dir, week_name)
                    if os.path.isdir(__curr_dir) is False:
                        continue

                    course_material[topic_name][_type]["week_names"].append(week_name)
                    course_material[topic_name][_type][week_name] = {"subtopic_names": []}
                    for subtopic_name in sorted(os.listdir(__curr_dir)):
                        ___curr_dir = os.path.join(__curr_dir, subtopic_name)
                        if os.path.isdir(___curr_dir) is False:
                            continue
                        
                        course_material[topic_name][_type][week_name]["subtopic_names"].append(
                            subtopic_name)
                        if subtopic_name not in course_material[topic_name][_type][week_name]:
                            course_material[topic_name][_type][week_name][subtopic_name] = {}
                        
                        for file_name in sorted(os.listdir(___curr_dir)):
                            file_path = os.path.join(___curr_dir, file_name)
                            extension = file_name.split('.')[-1]
                            if os.path.isfile(file_path):
                                if extension == "mp4":
                                    course_material[topic_name][_type][week_name][subtopic_name]["video_file"] = file_path
                                elif extension == "pdf":
                                    course_material[topic_name][_type][week_name][subtopic_name]["doc_file"] = file_path
                                elif extension == "vtt":
                                    course_material[topic_name][_type][week_name][subtopic_name]["subtitle_file"] = file_path
                            else:
                                dir_path = Path(file_path)
                                if dir_path.stem == 'short_clips':
                                    video_clip_paths = []
                                    for video_clip_path in dir_path.glob("*.mp4"):
                                        video_clip_paths.append(str(video_clip_path))
                                    course_material[topic_name][_type][week_name][subtopic_name]["video_clips"] = video_clip_paths

            elif _type == "Viva-Material":
                course_material[topic_name][_type] = {"context_files": []}
                for file_name in sorted(os.listdir(_curr_dir)):
                    file_path = os.path.join(_curr_dir, file_name)
                    extension = file_name.split('.')[-1]
                    if os.path.isfile(file_path):
                        if extension == "txt":
                            course_material[topic_name][_type]["context_files"].append(
                                file_path
                            )                
    
    return course_material


def time_to_seconds(time_string):
    # Parse the time string and create a datetime object
    time_obj = datetime.strptime(time_string, "%H:%M:%S.%f")
    
    # Extract the total seconds from the datetime object
    seconds = (time_obj.hour * 3600) + (time_obj.minute * 60) + time_obj.second + (time_obj.microsecond / 1000000)
    return int(seconds)
