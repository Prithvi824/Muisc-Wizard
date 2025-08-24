"""
This file contains the Youtube manager class that is responsible for all the interactions with youtube
"""

# 1st party imports
import re
import os
import logging
from typing import Optional, Tuple, Dict

# 3rd party imports
import requests
from googleapiclient.discovery import build

# local imports
from utilities.pydantic_models import SongYtInfo
from config import YOUTUBE_API_KEY, YT_TO_MP3_API_URL, QUERY_PARAM, API_KEY_HEADERS, SONG_DIR


class YtManager:
    """
    This class is responsible for all the interactions with youtube.
    """

    def __init__(self):
        """
        Initialize a YtManager object to interact with yt apis and perform actions related to youtube.

        Attributes:
            regex_pattern (str): The regex pattern to extract the video id from the url
        """

        # public data
        self.regex_pattern = r"(?:youtu\.be\/|youtube\.com(?:\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=|shorts\/)|youtu\.be\/|embed\/|v\/|m\/|watch\?(?:[^=]+=[^&]+&)*?v=))([^\"&?\/\s]{11})"

        # private data
        self.__API_KEY = YOUTUBE_API_KEY
        self.__YT_TO_MP3_API_URL = YT_TO_MP3_API_URL
        self.__YT_TO_MP3_QUERY_PARAM = QUERY_PARAM
        self.__YT_TO_MP3_API_KEY_HEADERS = API_KEY_HEADERS
        self.SONGS_DOWNLOAD_DIR = SONG_DIR

        # build the YouTube v3 API client
        self.__youtube_client = build("youtube", "v3", developerKey=self.__API_KEY)

        # setup logger
        self.logger = logging.getLogger(__name__)

    def get_video_id_from_url(self, url: str) -> Optional[str]:
        """
        Get the video id from the url. This function uses regex to extract the video id from the url.

        Args:
            url (str): The url of the video. e.g. https://www.youtube.com/watch?v=VIDEO_ID

        Returns:
            Optional[str]: The video id if found else None
        """

        # search for the video id in the url
        match = re.search(self.regex_pattern, url)

        # return the video id if found else None
        return match.group(1) if match else None

    def get_yt_info(self, video_id: str) -> Optional[SongYtInfo]:
        """
        Fetches YouTube video information using the YouTube v3 API.

        Args:
            video_id (str): The YouTube video ID.

        Returns:
            Optional[SongYtInfo]: The YouTube video information or None if the request failed.
        """

        try:
            # fetch the video information
            request = self.__youtube_client.videos().list(part="snippet", id=video_id)
            response = request.execute()

            # extract the video information
            item = response["items"][0]["snippet"]
            return SongYtInfo(
                author=item["channelTitle"],
                thumbnail=item["thumbnails"]["high"]["url"],
            )
        except Exception as e:
            # log the error if the request fails
            self.logger.error("Error fetching video id: %s. Error: %s", video_id, e)
            return None

    def download_song_via_video_id(self, video_id: str) -> Optional[Tuple[str, str]]:
        """
        Get the song from the YouTube URL.
        This function is used to get the mp3 song from the YouTube video ID.

        Args:
            video_id (str): The YouTube video ID to fetch the song from.

        Returns:
            Optional[Tuple[str, str]]: The path of the song and the title if successful, None otherwise.
        """

        # construct the API URL
        params = {self.__YT_TO_MP3_QUERY_PARAM: video_id}

        # make a GET request to the YouTube to MP3 API
        response = requests.get(
            url=self.__YT_TO_MP3_API_URL,
            headers=self.__YT_TO_MP3_API_KEY_HEADERS,
            params=params,
        )

        # check if the response is successful
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error(
                f"Error fetching song from YouTube: {response.text} - {e}"
            )
            return None

        # extract the data
        response_data: Dict[str, str] = response.json()
        download_url = response_data.get("link")
        title = response_data.get("title")

        # check if the download URL is present
        if not all([download_url, title]):
            self.logger.error("download link or title missing in the response.")
            return None

        # Make a GET request to download the song
        song_response = requests.get(download_url)

        # check if the song response is successful
        try:

            # raise an error if the response is not successful
            song_response.raise_for_status()

            # save the song locally
            path = os.path.join(self.SONGS_DOWNLOAD_DIR, f"{title}.mp3")
            with open(path, "wb") as song_file:
                song_file.write(song_response.content)

        except requests.HTTPError as e:
            self.logger.error(f"Error downloading song: {response.text} - {e}")
            return None

        # return the song path and title
        self.logger.info(
            f"Successfully fetched song: {title} from YouTube and saved at: {path}."
        )
        return path, title
