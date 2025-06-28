"""
This is the main file for the project.
It contains the main function and the main logic for the project.
"""

# 1st party imports
import os
import re
from http import HTTPStatus

# 3rd party imports
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, Query, Depends, UploadFile, File

# local imports
from config import SONG_DIR
from database.models import Song
from utilities.logger import logger
from wizard.wizard import MusicWizard
from database.database import api_get_session
from utilities.util import get_yt_info, convert_to_mp3
from utilities.pydantic_models import ApiResponse, ApiStatus

# create an instance of the MusicWizard class
WIZARD = MusicWizard()

APP = FastAPI(
    title="Music Wizard",
    description="A music wizard that can create and match fingerprints of songs.",
    version="0.1.0",
    docs_url="/docs",
    root_path="/backend"
)

# Add CORS middleware to the FastAPI app
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@APP.get("/add-song")
def add_song(yt_url: str = Query(...), session: Session = Depends(api_get_session)):
    """
    Endpoint to add a song to the database.
    """

    # clean the yt url
    regex_pattern = r"v=([^&]+)"
    match = re.search(regex_pattern, yt_url)
    if not match:

        # create an response model
        response = ApiResponse(
            status=ApiStatus.ERROR,
            error="Invalid YouTube URL. Please provide a valid YouTube video URL.",
        )

        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=response.model_dump(mode="json", exclude_none=True),
        )

    # extract the video ID from the URL
    video_id = match.group(1)

    # check if the song already exists in the database
    db_song = session.query(Song).filter(Song.yt_url == video_id).first()
    if db_song:
        logger.info(f"Song with video ID {video_id} already exists in the database.")

        # create an response model
        response = ApiResponse(
            status=ApiStatus.SUCCESS,
            data={
                "title": db_song.title,
                "yt_url": "https://www.youtube.com/watch?v=" + db_song.yt_url,
                "thumbnail": db_song.thumbnail,
                "artist": db_song.artist,
            },
            error="Song already exists in the database.",
        )

        return JSONResponse(
            status_code=HTTPStatus.ALREADY_REPORTED,
            content=response.model_dump(mode="json", exclude_none=True),
        )

    # get the song file from the YouTube to MP3 API
    path_and_title = WIZARD.get_song_from_yt_url(video_id)
    if not path_and_title:
        logger.error(f"Failed to download song from YouTube for video ID: {video_id}")

        # create an response model
        response = ApiResponse(
            status=ApiStatus.ERROR,
            error="Failed to download song from YT.",
        )

        # return the error response
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=response.model_dump(mode="json", exclude_none=True),
        )

    # unpack the song content and title
    song_path, title = path_and_title

    # get the YouTube video information
    yt_info = get_yt_info(video_id)
    if not yt_info:
        logger.error(
            f"Failed to fetch YouTube video information for video ID: {video_id}"
        )

        # create an response model
        response = ApiResponse(
            status=ApiStatus.ERROR,
            error="Failed to fetch YouTube video information.",
        )

        # return the error response
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=response.model_dump(mode="json", exclude_none=True),
        )

    # create fingerprints from the song content
    try:
        new_song_id = WIZARD.create_and_store_fingerprint(
            title=title,
            path=song_path,
            author=yt_info.author,
            thumbnail=str(yt_info.thumbnail),
            video_id=video_id,
        )
    except Exception as e:
        logger.error(f"Error processing video id - {video_id}: {e}")

        # clean up the song file after processing
        if os.path.exists(song_path):
            os.remove(song_path)

        # create an response model
        response = ApiResponse(
            status=ApiStatus.ERROR,
            error="Error processing the song file.",
        )

        # return the error response
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={"message": "Error processing the song file."},
        )

    # clean up the song file after processing
    if os.path.exists(song_path):
        os.remove(song_path)

    # create a success response
    logger.info(f"Song with video ID {video_id} added successfully to the database.")
    response = ApiResponse(
        status=ApiStatus.SUCCESS,
        data={
            "title": title,
            "yt_url": "https://www.youtube.com/watch?v=" + video_id,
            "thumbnail": str(yt_info.thumbnail),
            "artist": yt_info.author,
            "song_id": new_song_id
        },
    )

    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=response.model_dump(mode="json", exclude_none=True),
    )


@APP.post("/match-audio")
async def match_audio(
    file: UploadFile = File(...), session: Session = Depends(api_get_session)
):
    """
    Endpoint to match an uploaded audio file against the database.
    This endpoint accepts an audio file and attempts to match it against the fingerprints stored in the database.

    Args:
        file (UploadFile): The audio file to be matched.
        session (Session): The database session.

    Returns:
        JSONResponse: A response indicating whether a match was found or not.
    """

    # Check if the uploaded file is an audio file
    if not file.content_type.startswith("audio/"):

        # create an error response
        response = ApiResponse(
            status=ApiStatus.ERROR,
            error="Invalid file type. Please upload an audio file.",
        )

        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=response.model_dump(mode="json", exclude_none=True),
        )

    try:
        # Read the contents of the uploaded file
        contents = await file.read()

        # save the file locally
        file_path = f"{SONG_DIR}/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)

        # convert it to mp3
        file_path = convert_to_mp3(file_path)

        # match the audio from database
        match_results = WIZARD.create_and_match_fingerprint_from_db(file_path)

        # Clean up the mp3 file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        if match_results:
            # create a success response
            response = ApiResponse(
                status=ApiStatus.SUCCESS,
                data=[match_result.model_dump(mode="json") for match_result in match_results],
            )

            # return the response
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content=response.model_dump(mode="json", exclude_none=True),
            )
        else:

            # create a success response
            response = ApiResponse(
                status=ApiStatus.SUCCESS,
                error="No match found.",
            )

            # return the response
            return Response(status_code=HTTPStatus.NO_CONTENT)
    except Exception as e:

        # Clean up the file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        logger.error(f"Error matching audio file: {e}")

        # create an error response
        response = ApiResponse(
            status=ApiStatus.ERROR,
            error="Error processing the audio file.",
        )

        # return the error response
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=response.model_dump(mode="json", exclude_none=True),
        )


@APP.get("/songs")
def get_all_songs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    session: Session = Depends(api_get_session),
):
    """
    Endpoint to get all songs from the database with pagination.
    """

    # get all songs from the database with pagination
    songs = session.query(Song).offset(skip).limit(limit).all()
    total = session.query(Song).count()

    # create the resulting array
    result = [
        {
            "title": song.title,
            "artist": song.artist,
            "yt_url": song.yt_url,
            "thumbnail": song.thumbnail,
        }
        for song in songs
    ]

    # create a response
    response = ApiResponse(
        status=ApiStatus.SUCCESS,
        data={
            "total": total,
            "count": len(result),
            "songs": result,
        },
    )

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=response.model_dump(mode="json", exclude_none=True),
    )
