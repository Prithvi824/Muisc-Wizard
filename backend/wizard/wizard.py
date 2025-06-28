"""
This file contains the logic for the MusicWizard.
"""

# 1st party imports
import os
from collections import defaultdict, Counter
from typing import List, Tuple, Optional, Dict

# 3rd party imports
import librosa
import requests
import numpy as np
from scipy.ndimage import maximum_filter
from scipy.signal import butter, lfilter

# local imports
from utilities.logger import logger
from database.database import get_sync_session
from database.models import Song, SongFingerPrints
from utilities.pydantic_models import SongDbInfo
from config import (
    YT_TO_MP3_API_URL,
    QUERY_PARAM,
    API_KEY_HEADERS,
    SONG_DIR,
    SAMPLING_RATE,
    CONFIDENCE_THRESHOLD,
)


class MusicWizard:
    """
    The MusicWizard class provides functionality to generate audio fingerprints from music files,
    store them in a database, and match new audio inputs against stored fingerprints.
    It supports extracting audio features, creating robust hashes from frequency peaks,
    and efficiently searching for song matches using those hashes.

    Attributes:
        hop_length (int): The hop length for STFT (number of samples between successive frames).
        frame_rate (float): The frame rate derived from the sampling rate and hop length.
        fan_value (int): Number of pairs to generate for each anchor point in fingerprinting.
        neighborhood (Tuple[int]): The size of the neighborhood to consider for local peak detection.
        threshold (int): The threshold value for considering a frequency as a peak.
        song_dir (str): Directory path for storing downloaded or processed songs.
        min_time_delta (int): Minimum allowed time difference between paired peaks for hashing.
        max_time_delta (int): Maximum allowed time difference between paired peaks for hashing.

    Methods:
        create_time_series_from_file(path, sampling_rate): Loads audio and returns time series and sampling rate.
        apply_stft(time_series): Generates a spectrogram from a time series using STFT.
        get_peak_points(spectrogram, neighborhood): Finds frequency peaks in the spectrogram.
        generate_hash(freq1, freq2, delta_time): Computes a hash for a frequency pair and time delta.
        create_fingerprint(spectrogram): Converts a spectrogram into a list of fingerprint hashes.
        create_and_store_fingerprint(title, path, author, thumbnail, video_id): Stores fingerprints in the database.
        match_fingerprints_from_db(fingerprint): Finds the best matching song for given fingerprints.
        get_song_from_yt_url(video_id): Downloads a song from YouTube using a video ID.
        create_and_match_fingerprint_from_db(path): Matches an audio file against stored fingerprints.
    """

    def __init__(
        self,
        fan_value: int = 9,
        neighborhood: Tuple[int] = (19, 19),
        hop_length: int = 412,
        min_time_delta: int = 1,
        max_time_delta: int = 30,
    ):
        """
        Initialize the MusicWizard class.
        This class is used to create and match fingerprints from audio files.
        """

        # set the default hop length
        self.hop_length = hop_length

        # set the default frame length
        self.frame_rate = SAMPLING_RATE / self.hop_length

        # tunable parameters
        self.fan_value = fan_value
        self.neighborhood = neighborhood

        # create the directory for storing the downloaded songs
        self.song_dir = SONG_DIR

        # set the minimum and maximum time delta between two peaks
        self.min_time_delta = min_time_delta
        self.max_time_delta = max_time_delta

    def create_time_series_from_file(
        self, path: str, sampling_rate: int = SAMPLING_RATE
    ) -> Tuple[np.ndarray, int]:
        """
        Create a time series from the provided audio file.
        The time series is created by loading the audio file and resampling it to the specified sampling rate.
        This returns the audio time series and the sampling rate.

        sr is the number of samples per second (the sampling rate)

        Args:
            path (str): The path to the audio file.
            sampling_rate (int): The sampling rate to resample the audio file to. Defaults to SAMPLING_RATE.

        Returns:
            Tuple(List[float], int): A numpy array containing the amplitude of the audio signal at each time step,
            and the sampling rate.
        """

        return librosa.load(path, sr=sampling_rate)

    def apply_bandpass_filter(
        self,
        time_series: np.ndarray,
        lowcut: float = 200.0,
        highcut: float = 5000.0,
        order: int = 5,
    ) -> np.ndarray:
        """
        Apply a bandpass filter to the provided time series.

        The bandpass filter removes noise by allowing only frequencies
        between `lowcut` and `highcut` Hz to pass through.

        Args:
            time_series (np.ndarray): The audio signal as a 1D NumPy array.
            lowcut (float): Lower cutoff frequency in Hz. Defaults to 300.0.
            highcut (float): Upper cutoff frequency in Hz. Defaults to 3000.0.
            order (int): The order of the filter (steepness). Defaults to 5.

        Returns:
            np.ndarray: The filtered audio signal.
        """

        nyquist = 0.5 * SAMPLING_RATE
        low = lowcut / nyquist
        high = highcut / nyquist

        # if high is greater than or equal to one bring it down
        if high >= 1:
            high = 0.999
        band = (low, high)

        # Get filter coefficients
        numerator, denominator = butter(order, band, btype="band")

        # Apply filter
        return lfilter(numerator, denominator, time_series)

    def preprocess_time_series(self, time_series: np.ndarray) -> np.ndarray:
        """
        Preprocess the time series by normalizing it.

        Args:
            time_series (np.ndarray): The time series to preprocess.

        Returns:
            np.ndarray: The preprocessed time series.
        """

        # Normalize the time series
        if np.max(np.abs(time_series)) > 0:
            time_series = time_series / np.max(np.abs(time_series))

        # trim silence from the beginning and end of the time series
        time_series, _ = librosa.effects.trim(time_series, top_db=20)

        # apply bandpass filter to the time series
        time_series = self.apply_bandpass_filter(time_series)

        return time_series

    def apply_stft(self, time_series: np.ndarray, n_fft: int = 2048) -> np.ndarray:
        """
        Apply Short-Time Fourier Transform (STFT) to the provided time series.
        The STFT is used to convert the time series into a spectrogram.
        The spectrogram is a 2D representation of the time series, where the x-axis represents time,
        the y-axis represents frequency, and the color represents the amplitude of the frequency at that time.

        Args:
            time_series (np.ndarray): The time series to apply STFT to.

        Returns:
            np.ndarray: The spectrogram of the time series.
        """

        # preprocess the given audio time series
        preprocessed_time_series = self.preprocess_time_series(time_series)

        # Apply STFT to the time series
        spectogram = librosa.stft(
            preprocessed_time_series, n_fft=n_fft, hop_length=self.hop_length
        )

        # Convert the spectrogram's values from complex numbers to float
        spectogram = np.abs(spectogram)

        # Convert the spectrogram's values from complex numbers to float
        spectogram = librosa.amplitude_to_db(spectogram, ref=np.max)

        return spectogram

    def get_peak_points(
        self, spectrogram: np.ndarray, neighborhood: Tuple[int]
    ) -> List[Tuple[int, int]]:
        """
        Get the peak points from the provided spectrogram.
        The peak points are the maximum frequency in a neighborhood around each time step.

        Args:
            spectrogram (np.ndarray): The spectrogram to get peak points from.
            neighborhood (int): The size of the neighborhood to consider for each time step.

        Returns:
            List(Tuple[int, int]): A list of tuples containing the frequency and time step of each peak point.
        """

        # apply local maxima on the spectrogram
        locally_maximized_spectrogram = maximum_filter(spectrogram, size=neighborhood)

        # Turn all the local max to true and other to false in a matrix
        peaks_only_matrix = spectrogram == locally_maximized_spectrogram

        # calculate the average of the peaks and use it as a threshold
        threshold = spectrogram[peaks_only_matrix].mean()

        # Get the indices of the local maxima
        peaks_cords = np.argwhere(peaks_only_matrix & (spectrogram >= threshold))

        # returns [(0, 0), (1, 1), ...]
        return peaks_cords

    def generate_hash(self, freq1: int, freq2: int, delta_time: int) -> int:
        """
        Generate a hash from the provided frequency and time step.
        The hash is generated by combining the frequency and time step into a single integer.
        We shift freq1 and freq2 by 18 and 8 bits respectively and combine them with delta_time and freq1_time.
        By shiftting we mean add 0s to the right of the number and then convert its value from binary to decimal.

        Example:

            freq1 = 1, freq2 = 2, delta_time = 3, freq1_time = 4

            generated_hash = (1 << 18) | (2 << 8) | 3 | 4 = 262663

        Args:
            freq1 (int): The first frequency.
            freq2 (int): The second frequency.
            delta_time (int): The time difference between the two frequencies.

        Returns:
            int: The generated hash.
        """

        return (freq1 << 18) | (freq2 << 8) | delta_time

    def decode_hash(self, hash_value: int) -> Tuple[int, int, int]:
        """
        Decode the provided hash into its components.
        The hash is decoded by extracting the frequency and time step from the combined integer.

        Args:
            hash_value (int): The hash value to decode.

        Returns:
            Tuple[int, int, int]: A tuple containing the frequency1, frequency2 and delta_time.
        """

        # decode the hash value
        delta_time = hash_value & 0xFF
        freq2 = hash_value >> 8 & 0x3FF
        freq1 = hash_value >> 18 & 0x3FF

        return freq1, freq2, delta_time

    def create_fingerprint(self, spectrogram: np.ndarray) -> List[Tuple[int, int]]:
        """
        Create a fingerprint from the provided spectrogram.
        The fingerprint is created by taking the maximum frequency in a neighborhood around each time step
        and generating a hash from the frequency and time step.

        Fingerprints are tuples of (hash, time_step) where:
            - hash is the generated hash from the frequency and time step.
            - time_step is the time step of the peak point in the spectrogram.

        Args:
            spectrogram (List[List[float]]): The spectrogram to create a fingerprint from.

        Returns:
            List[Tuple[int, int]]: A list of tuples containing the generated hash and the time step.
        """

        # Get the peak points from the spectrogram
        peaks = self.get_peak_points(spectrogram, self.neighborhood)

        # Create a list to store the fingerprints
        fingerprints = []

        # Iterate over the peak points
        for anchor_idx in range(0, len(peaks)):

            # Get the frequency and time step of the first peak point
            freq_bin1, time1 = peaks[anchor_idx]

            # match this anchor point with the next `N fan_values` peak points
            for pair_indx in range(1, self.fan_value + 1):

                # get the frequency and time step of the second peak point
                if anchor_idx + pair_indx >= len(peaks):
                    # skip if there are no forward pairs left
                    continue

                # Get the frequency and time step of the second peak point
                freq_bin2, time2 = peaks[anchor_idx + pair_indx]

                # Calculate the delta time between the anchor peak and pair peak points
                delta_time = time2 - time1

                # Skip if the delta time is less than the step difference
                if delta_time < self.min_time_delta or delta_time > self.max_time_delta:
                    continue

                # Generate a hash from the frequency and time step
                generated_hash = self.generate_hash(freq_bin1, freq_bin2, delta_time)

                # Append the generated hash to the fingerprints list
                fingerprints.append((int(generated_hash), int(time1)))

        # Sort the fingerprints list by the time step
        fingerprints.sort(key=lambda x: x[1])

        return fingerprints

    def create_and_store_fingerprint(
        self,
        title: str,
        path: str,
        author: str,
        thumbnail: str,
        video_id: str,
    ) -> int:
        """
        Create and store the fingerprint in the database.
        This function is used to create a fingerprint from the provided audio file
        and store it in the database.

        Args:
            title (str): The title of the song.
            path (str): The path to the audio file.
            author (str): The author of the song.
            thumbnail (str): The thumbnail URL of the song.
            video_id (str): The YouTube video ID of the song.

        Returns:
            int: The ID of the song in the database.
        """

        # Create a time series from the provided audio file
        time_series, d = self.create_time_series_from_file(path, SAMPLING_RATE)

        # Apply STFT to the time series
        spectrogram = self.apply_stft(time_series)

        # Create a fingerprint from the spectrogram
        fingerprints = self.create_fingerprint(spectrogram)

        # log the storing to db
        logger.info(
            f"Storing {len(fingerprints)} fingerprints for song: {title} in the database."
        )

        # Store the fingerprint in the database
        with get_sync_session() as session:

            # create a new song object
            song = Song(
                title=title, yt_url=video_id, artist=author, thumbnail=thumbnail
            )

            # Create a list of SongFingerPrints objects
            song_fingerprints = [
                SongFingerPrints(
                    fingerprint_index=time_step, fingerprint_hash=hash_value, song=song
                )
                for hash_value, time_step in fingerprints
            ]

            try:
                # Add the song and the fingerprints to the session
                session.add(song)
                session.add_all(song_fingerprints)

                # Commit the session
                session.commit()
                session.refresh(song)

            except Exception as e:
                logger.error(f"Error storing fingerprints in the database: {e}")
                session.rollback()

        return song.id

    def match_fingerprints_from_db(
        self, fingerprint: List[Tuple[int, int]]
    ) -> Optional[List[Tuple[int, int, int]]]:
        """
        Match the provided fingerprints.
        The fingerprints are matched by iterating over the fingerprints from database
        and finding all the matches.

        Args:
            fingerprint (List[Tuple[int, int]]): The fingerprint to match against the db.

        Returns:
            Optional[List[Tuple[int, int, int]]]: A list of tuples (song_id, timestamp, confidence)
                representing potential matches if any else None.
        """

        # votes dictionary
        votes = defaultdict(Counter)

        # convert the hash values to a dictionary
        # hash_values = {hash_value: [time_step1, time_step2, ...]}
        hash_values = defaultdict(list)
        for h, t in fingerprint:
            hash_values[h].append(t)

        # create a sync session
        with get_sync_session() as session:

            # get all matches from the db
            query_output = (
                session.query(
                    SongFingerPrints.fingerprint_hash,
                    SongFingerPrints.fingerprint_index,
                    SongFingerPrints.song_id,
                )
                .filter(SongFingerPrints.fingerprint_hash.in_(hash_values.keys()))
                .all()
            )

            # Before voting tune the hashes to remove common hashes
            hash_threshold = len(query_output) * 0.10
            hash_counter = Counter([h for h, _, _ in query_output])
            filtered_hashes = [
                (hash, idx, song_id)
                for hash, idx, song_id in query_output
                if hash_counter[hash] < hash_threshold
            ]

            # vote for the best match
            for db_hash, db_offset, db_song_id in filtered_hashes:

                # for each hash value in the fingerprint get the timestamps
                for timestamp in hash_values[db_hash]:

                    # calculate the delta time
                    delta = db_offset - timestamp

                    # dont count negative deltas
                    if delta < 0:
                        continue
                    votes[db_song_id][delta] += 1

        # get the best 3 matches
        match_candidates: List[Tuple[int, int, int]] = []

        # iterate over the votes
        for song_id, counter in votes.items():

            # get the most common delta and count
            delta, count = counter.most_common(1)[0]
            match_candidates.append((song_id, delta, count))

        # sort by count descending and take top 3
        top_matches = sorted(match_candidates, key=lambda x: x[2], reverse=True)[:3]

        results = []
        for song_id, delta, count in top_matches:
            # get the timestamp and add to result
            timestamp = abs(delta or 0) / self.frame_rate

            # check confidence and add to result
            confidence = count / max(1, len(filtered_hashes))

            if confidence >= CONFIDENCE_THRESHOLD:
                results.append((song_id, timestamp, confidence))

        return results if results else None

    def get_song_from_yt_url(self, video_id: str) -> Optional[Tuple[str, str]]:
        """
        Get the song from the YouTube URL.
        This function is used to get the mp3 song from the YouTube URL.

        Args:
            video_id (str): The YouTube video ID to fetch the song from.

        Returns:
            Optional[Tuple[str, str]]: The path of the song and the title if successful, None otherwise.
        """

        # construct the API URL
        url = YT_TO_MP3_API_URL
        params = {QUERY_PARAM: video_id}

        # make a GET request to the YouTube to MP3 API
        response = requests.get(url, headers=API_KEY_HEADERS, params=params)

        # check if the response is successful
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(f"Error fetching song from YouTube: {response.text} - {e}")
            return None

        # extract the data
        response_data: Dict[str, str] = response.json()
        download_url = response_data.get("link")
        title = response_data.get("title")

        # check if the download URL is present
        if not download_url or not title:
            logger.error("download link or title missing in the response.")
            return None

        # Make a GET request to download the song
        song_response = requests.get(download_url)

        # check if the song response is successful
        try:

            # raise an error if the response is not successful
            song_response.raise_for_status()

            # save the song locally
            path = os.path.join(self.song_dir, f"{title}.mp3")
            with open(path, "wb") as song_file:
                song_file.write(song_response.content)

        except requests.HTTPError as e:
            logger.error(f"Error downloading song: {response.text} - {e}")
            return None

        # return the song path and title
        logger.info(
            f"Successfully fetched song: {title} from YouTube and saved at: {path}."
        )
        return path, title

    def create_and_match_fingerprint_from_db(
        self, path: str
    ) -> Optional[List[SongDbInfo]]:
        """
        Generates an audio fingerprint from the provided audio file and attempts to match it against fingerprints stored in the database.

        Steps performed:
            1. Loads the audio file from the given path and creates a time series.
            2. Applies Short-Time Fourier Transform (STFT) to generate a spectrogram.
            3. Creates a fingerprint from the spectrogram.
            4. Searches the database for the best matching fingerprint.
            5. If a match is found, retrieves the corresponding song information from the database.

        Args:
            path (str): The file path to the audio file to be fingerprinted and matched.

        Returns:
            Optional(SongDbInfo):
                A pydantic model containing the song info. None if no match is found.
        """
        # create a time series from the provided audio file
        time_series, _ = self.create_time_series_from_file(path, SAMPLING_RATE)

        # apply STFT to the time series
        spectrogram = self.apply_stft(time_series)

        # create a fingerprint from the spectrogram
        fingerprints = self.create_fingerprint(spectrogram)

        # match the fingerprints from the database
        matches = self.match_fingerprints_from_db(fingerprints)

        # if no match is found, return None
        if not matches:
            return None

        # create the resulting array
        matching_result = []

        # create a db session to fetch from db
        with get_sync_session() as session:

            for song_id, timestamp, confidence in matches:

                # get the song from db and add to results
                song = session.query(Song).filter(Song.id == song_id).first()

                logger.info("Matched song: %s, with confidence: %s", song.title, confidence)

                # return the title, yt_url and timestamp of the best match
                matching_result.append(
                    SongDbInfo(
                        title=song.title,
                        yt_url=song.yt_url,
                        thumbnail=song.thumbnail,
                        artist=song.artist,
                        timestamp=timestamp,
                    )
                )

        return matching_result
