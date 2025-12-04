"""
This file contains the configuration for the project.
"""

# 1st party imports
import os
from typing import Dict, Any

# 3rd party imports
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# load environment variables from .env file
load_dotenv()

# The database schema to use
DB_SCHEMA = "music_wizard"


class Settings(BaseSettings):
    """
    This class consists of all the configuration variables for the project.
    """

    DB_STRING: str = Field(
        default=os.getenv("DB_STRING"),
        description="The url connection string to connect to the database.",
    )

    ECHO_SQL: bool = Field(
        default=os.getenv("ECHO_SQL", False),
        description="The echo sql flag to enable or disable the echo sql.",
    )

    YT_TO_MP3_URL: str = Field(
        default=os.getenv("YT_TO_MP3_URL"),
        description="The url of the yt to mp3 api.",
    )

    QUERY_PARAM_YT_TO_MP3_URL: str = Field(
        default=os.getenv("QUERY_PARAM_YT_TO_MP3_URL", "id"),
        description="The query parameter for the yt to mp3 api.",
    )

    RAPID_API_KEY: str = Field(
        default=os.getenv("RAPID_API_KEY"),
        description="The rapid api key for the rapid api.",
    )

    RAPID_API_HOST: str = Field(
        default=os.getenv("RAPID_API_HOST"),
        description="The rapid api host for the rapid api.",
    )

    SONG_DIR: str = Field(
        default=os.getenv("SONG_DIR", "downloaded_songs"),
        description="The directory for storing songs.",
    )

    SAMPLE_RATE: int = Field(
        default=int(os.getenv("SAMPLE_RATE", 44100)),
        description="The sample rate for audio processing.",
    )

    CONFIDENCE_THRESHOLD: float = Field(
        default=float(os.getenv("CONFIDENCE_THRESHOLD", 0.00)),
        description="The confidence threshold for matching fingerprints.",
    )

    YOUTUBE_API_KEY: str = Field(
        default=os.getenv("YOUTUBE_API_KEY"),
        description="The official youtube api key for fetching details from youtube.",
    )

    API_KEY_HEADERS: Dict[str, Any] = Field(
        default={
            "x-rapidapi-host": os.getenv("RAPID_API_HOST"),
            "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
        },
        description="The api key headers for the rapid api.",
    )

    DB_SCHEMA: str = Field(
        default=DB_SCHEMA,
        description="The schema for the database.",
    )


# create a instance to be used everywhere
project_settings = Settings()

# Override DB_STRING to include schema options
base_db_string = os.getenv("DB_STRING")
if base_db_string and "?options=" not in base_db_string:
    project_settings.DB_STRING = base_db_string + f"?options=-csearch_path={DB_SCHEMA}"

# create the download directory if it does not exist
os.makedirs(project_settings.SONG_DIR, exist_ok=True)
