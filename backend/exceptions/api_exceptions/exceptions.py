"""
This file contains the custom exceptions for the API.
"""

# 1st party imports
from http import HTTPStatus

# 3rd party imports
from fastapi import HTTPException


class InvalidUrlError(HTTPException):
    """
    Custom exception for invalid yt urls received in apis.
    """

    def __init__(self, detail: str = None):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class YtInfoFetchError(HTTPException):
    """
    Custom exception for failed yt info fetch.
    """

    def __init__(self, detail: str = None):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class SongDownloadError(HTTPException):
    """
    Custom exception for failed song download.
    """

    def __init__(self, detail: str = None):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class FingerprintError(HTTPException):
    """
    Custom exception for failed fingerprint creation.
    """

    def __init__(self, detail: str = None):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class InvalidFileTypeError(HTTPException):
    """
    Custom exception for invalid file type received in apis.
    """

    def __init__(self, detail: str = None):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class InternalServerError(HTTPException):
    """
    Custom exception for internal server error.
    """

    def __init__(self, detail: str = None):
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail)