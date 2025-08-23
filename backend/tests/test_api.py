"""
This file contains the test cases for the API.
"""

# 1st party imports
from httpx import Response
from http import HTTPStatus

# 3rd party imports
from fastapi.testclient import TestClient


class TestAddSongEndpoint:
    """
    This class contains the test cases for the add song endpoint.

    endpoint: /add-song
    method: POST
    """

    API_URL = "/add-song"

    def __register_song(self, client: TestClient, url: str) -> Response:
        """
        This function is used to register a song in the database.

        Args:
            client (TestClient): The test client.
            url (str): The YouTube URL.

        Returns:
            Response: The response from the API.
        """

        # fetch the response
        response = client.get(self.API_URL, params={"yt_url": url})
        return response

    def test_add_song_valid_youtube_url(self, client: TestClient):
        """
        Test the add song endpoint with a valid YouTube URL.
        """

        # testing url
        test_url = "https://www.youtube.com/watch?v=VF-FGf_ZZiI"

        # fetch the response
        response = self.__register_song(client, test_url)

        # parse the response
        response_data = response.json()

        # check if the response is successful
        assert response.status_code == HTTPStatus.CREATED

        # check if the response data is valid
        assert response_data["status"] == "success"

    def test_add_song_invalid_youtube_url(self, client: TestClient):
        """
        Test the add song endpoint with an invalid YouTube URL.
        """

        # testing url
        test_url = "https://www.yt.com/randomc-3rm2"

        # fetch the response
        response = self.__register_song(client, test_url)

        # check if the response is successful
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_song_already_exists(self, client: TestClient):
        """
        Test the add song endpoint with a YouTube URL that already exists in the database.
        """

        # testing url
        test_url = "https://www.youtube.com/watch?v=dbPHCjZ-lHw"

        # fetch the response
        response_one = self.__register_song(client, test_url)

        # parse the response
        response_one_data = response_one.json()

        # check if the response is successful
        assert response_one.status_code == HTTPStatus.CREATED

        # check if the response data is valid
        assert response_one_data["status"] == "success"

        # fetch the response
        response_two = self.__register_song(client, test_url)

        # parse the response
        response_two_data = response_two.json()

        # check if the response is successful
        assert response_two.status_code == HTTPStatus.ALREADY_REPORTED

        # check if the response data is valid
        assert response_two_data["data"]["yt_url"] == test_url


class TestMatchAudioEndpoint:
    """
    This class contains the test cases for the match audio endpoint.

    endpoint: /match-audio
    method: POST
    """

    API_URL = "/match-audio"
    ADD_SONG_API_URL = "/add-song"
    TEST_SONG_VIDEO_ID = "vk6014HuxcE"
    TEST_SONG_URL = f"https://www.youtube.com/watch?v={TEST_SONG_VIDEO_ID}"

    def __register_song(self, client: TestClient) -> None:
        """
        This function is used to register a song in the database.

        Args:
            client (TestClient): The test client.
        """

        # register the song
        client.get(self.ADD_SONG_API_URL, params={"yt_url": self.TEST_SONG_URL})
        return None

    def __match_audio_file(self, client: TestClient, file_path: str) -> Response:
        """
        This function is used to match an audio file.

        Args:
            client (TestClient): The test client.
            file_path (str): The path to the audio file.

        Returns:
            Response: The response from the API.
        """

        # match the audio snippet
        with open(file_path, "rb") as audio_file:
            files = {"file": ("test_audio_snippet.mp3", audio_file, "audio/mp3")}
            response = client.post(self.API_URL, files=files)

        # return the response
        return response

    def test_match_correct_song(self, client: TestClient):
        """
        Test the match audio endpoint with a valid match.
        """

        # register the song
        self.__register_song(client)

        # match the audio snippet
        response = self.__match_audio_file(client, self.VALID_FILE_PATH)

        # parse the response
        response_data = response.json()

        # check if the response is successful
        assert response.status_code == HTTPStatus.OK

        # check if the response data is valid
        assert response_data["status"] == "success"

        print(f"\n\n{response_data}\n\n")

        # check the match result
        assert len(response_data["data"]) > 0
        assert response_data["data"][0]["yt_url"] == self.TEST_SONG_VIDEO_ID
        assert False
