"""
This file contains the configuration for the project.
"""

# 1st party imports
import os

# 3rd party imports
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# get the database URL from the environment variables
DB_URL = os.getenv("DB_STRING")

# SQL DEBUG
ECHO_SQL = os.getenv("ECHO_SQL", False)

# Yt to Mp3 API URL
YT_TO_MP3_API_URL = os.getenv("YT_TO_MP3_URL")
QUERY_PARAM = os.getenv("QUERY_PARAM_YT_TO_MP3_URL", "id")

# Rapid API key and host
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")

# RAPID API KEY HEADERS
API_KEY_HEADERS = {
    "x-rapidapi-host": os.getenv("RAPID_API_HOST"),
    "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
}

# Directory for storing songs
SONG_DIR = os.getenv("SONG_DIR", "downloaded_songs")
os.makedirs(SONG_DIR, exist_ok=True)

# Sample rate for audio processing
SAMPLING_RATE = int(os.getenv("SAMPLE_RATE", 44100))

# Set the confidence threshold for matching fingerprints
# TODO: A proper confidence level should have to be determined
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.00))

# check if all the required environment variables are set
req_vars = [DB_URL, YT_TO_MP3_API_URL, RAPID_API_KEY, RAPID_API_HOST]
if not all(req_vars):
    raise ValueError("All the environment variables are not set...")
