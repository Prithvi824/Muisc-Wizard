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

    def test_song_already_exists(self, client: TestClient, get_test_db):
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
