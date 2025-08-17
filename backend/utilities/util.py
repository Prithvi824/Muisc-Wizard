"""
This module contains utility functions for the wizard.io package.
"""

# 1st party imports
import os
import logging
import random
import subprocess

# setup logger
logger = logging.getLogger(__name__)


def convert_to_mp3(input_path: str, output_path: str = None) -> str:
    """
    Converts a audio file to .mp3 format using ffmpeg.

    Args:
        input_path (str): Path to the input file.
        output_path (str, optional): Path to save the output .mp3 file.
                                     If not provided, replaces extension with .mp3.

    Returns:
        str: Path to the converted .mp3 file.

    Raises:
        RuntimeError: If ffmpeg fails to convert the file.
    """

    # check if the file is already a mp3
    if input_path.endswith(".mp3"):
        return input_path

    # if output path is not provided, replace extension with .mp3
    if not output_path:
        output_path = (
            os.path.splitext(input_path)[0] + f"{random.randint(1, 100)}" ".mp3"
        )

    # build the command
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i",
        input_path,
        "-vn",  # Skip any video streams
        "-ab",
        "192k",  # Audio bitrate
        "-ar",
        "44100",  # Audio sampling rate
        "-f",
        "mp3",
        output_path,
    ]

    try:
        # Run the command and capture output and error
        subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # remove the file
        if os.path.exists(input_path):
            os.remove(input_path)

        # Return the output path
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg error: {e.stderr.decode()}")
