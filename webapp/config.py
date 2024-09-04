BASE_DIR = 'webapp/static'
DATASET_COURSE_BASE_DIR = "./dataset/courses/"

API_CONFIG = {
    # "server_host": "leap-api",
    "server_host": "localhost",
    "server_port": "8500",
    "ask_doubt":  {
        "max_answer_length": 30,
        "max_seq_length": 384,
        "top_n": 2,
        "top_k": 1
    },
    "ai_examiner": {
        "viva_ask_question_types": ["Open Ended", "Single Choice", "Multiple Choice", "Yes or No Choice"]
    }
}