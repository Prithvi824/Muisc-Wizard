"""
This module contains pydantic models for the wizard.io package.
"""

# 1st party imports
from enum import Enum
from typing import Optional, Dict, Any, List

# 3rd party imports
from pydantic import BaseModel, Field, HttpUrl


class SongYtInfo(BaseModel):
    """
    Pydantic model for YouTube song information.
    """

    author: str = Field(..., description="The name of the author of the song.")
    thumbnail: HttpUrl = Field(
        ..., description="The URL of the thumbnail image for the song."
    )


class SongDbInfo(BaseModel):
    """
    Pydantic model for song information stored in the database.
    """

    title: str = Field(..., description="The title of the song.")
    yt_url: str = Field(..., description="The YouTube ID of the song.")
    thumbnail: HttpUrl = Field(
        ..., description="The URL of the thumbnail image for the song."
    )
    artist: str = Field(..., description="The name of the artist of the song.")
    timestamp: float = Field(
        ..., description="The timestamp from where the part of the song begins."
    )


class ApiStatus(Enum):
    """
    Enum for API status.
    """

    SUCCESS = "success"
    ERROR = "error"


class ApiResponse(BaseModel):
    """
    Pydantic model for API response.
    """

    status: ApiStatus
    data: Optional[Dict[Any, Any] | List] = None
    error: Optional[str] = None
