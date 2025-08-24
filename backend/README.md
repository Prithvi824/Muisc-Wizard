# Music Wizard – Backend

A FastAPI-powered service that fingerprints songs, stores them in a SQL database, and later matches short audio clips to identify the track and timestamp.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Folder Structure](#folder-structure)
3. [Quick-start](#quick-start)
4. [Docker Deployment](#docker-deployment)
5. [Environment Variables](#environment-variables)
6. [API Reference](#api-reference)
7. [Internals](#internals)
8. [Deployment Notes](#deployment-notes)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

1. **Add song** – Download audio from YouTube, generate a fingerprint, and store hashes in the DB.
2. **Match audio** – Accept an uploaded clip, fingerprint it, search DB hashes, and return probable matches sorted by confidence.

The heavy lifting is done by `wizard/wizard.py`, which leverages Librosa, SciPy, and custom hashing.

---

## Folder Structure

```
backend/
├── alembic/              # DB migrations
├── database/             # SQLAlchemy models & session helpers
├── utilities/            # Logger, misc helpers, Pydantic schemas
├── wizard/               # Audio-fingerprinting engine
├── main.py               # FastAPI entry-point
├── config.py             # Environment-driven settings
├── requirements.txt      # Python deps (this file)
└── README.md             # You-are-here
```

---

## Quick-start

```bash
# 1. Python 3.10+ and FFmpeg must already be installed and in PATH.
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

# 2. Copy .env.example → .env and fill in keys (see next section)

# 3. Run database migrations
alembic upgrade head

# 4. Launch the API server
uvicorn backend.main:APP --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## Docker Deployment

### Building the Docker Image

The application includes a multi-stage Dockerfile for efficient containerization:

```bash
# Build the Docker image (run from the backend directory)
docker build -t music-wizard-backend .
```

### Running with Docker

Once the image is built, you can run the containerized application:

```bash
# Run the container with environment file
docker run -d -p 8000:8000 --env-file .env <img_id>

# Alternative: Run with individual environment variables
docker run -d -p 8000:8000 \
  -e DB_STRING="sqlite:///wizard.db" \
  -e RAPID_API_KEY="your_key_here" \
  -e RAPID_API_HOST="your_host_here" \
  -e YT_TO_MP3_URL="your_url_here" \
  <img_id>
```

**Important Notes:**

-   Ensure your `.env` file is in the same directory when using `--env-file .env`
-   The container exposes port 8000 and runs with Gunicorn using 4 workers
-   The application uses a distroless Python image for minimal attack surface
-   Downloaded songs and logs should be persisted using Docker volumes in production:
    ```bash
    docker run -d -p 8000:8000 --env-file .env \
      -v $(pwd)/downloaded_songs:/app/downloaded_songs \
      -v $(pwd)/logs:/app/logs \
      <img_id>
    ```

### Docker Architecture

The Dockerfile uses a two-stage build:

1. **Builder stage**: Uses `python:3.11.2-slim` to install dependencies and copy application code
2. **Runtime stage**: Uses `gcr.io/distroless/python3` for a minimal, secure runtime environment

The container runs the application using Gunicorn with Uvicorn workers for optimal performance.

---

## Environment Variables

Place these in a `.env` (loaded by `config.py`).
| Variable | Description |
|----------|-------------|
| `DB_STRING` | SQLAlchemy DB URI (e.g. `sqlite:///wizard.db` or Postgres URL). |
| `ECHO_SQL` | `'True'` enables SQL echo for debugging (optional). |
| `YT_TO_MP3_URL` | RapidAPI endpoint to convert YouTube → MP3. |
| `QUERY_PARAM_YT_TO_MP3_URL` | Query key (defaults to `id`). |
| `RAPID_API_KEY` | RapidAPI authentication key. |
| `RAPID_API_HOST` | RapidAPI host header. |
| `SONG_DIR` | Where downloaded songs are stored (`downloaded_songs` by default). |
| `SAMPLE_RATE` | Audio resample rate (default 44100). |
| `CONFIDENCE_THRESHOLD` | Minimum score to accept a match (float). |

---

## API Reference

### `GET /add-song`

Download and fingerprint a YouTube track.

| Query param | Type   | Description                             |
| ----------- | ------ | --------------------------------------- |
| `yt_url`    | string | Full YouTube URL or video ID parameter. |

Responses:

-   **200 OK / 208 ALREADY_REPORTED** – Song details.
-   **400** – Invalid URL.
-   **404** – Download or metadata fetch failed.

### `POST /match-audio`

Multipart upload of an audio clip. Returns list of candidate matches.

| Body   | Type   | Description                                            |
| ------ | ------ | ------------------------------------------------------ |
| `file` | binary | Audio file (any container; will be transcoded to MP3). |

Responses:

-   **200 OK** – JSON list of `{title, yt_url, thumbnail, artist, timestamp}` ordered by confidence.
-   **204 NO_CONTENT** – No match.
-   **400** – Not an audio file.

### `GET /songs`

Paginated list of songs.

| Query param | Default | Description                    |
| ----------- | ------- | ------------------------------ |
| `skip`      | 0       | Records to skip.               |
| `limit`     | 10      | Max records to return (1-100). |

---

## Internals

-   **`wizard/wizard.py`** – Core fingerprinting: STFT → peak picking → hash pairs → DB store/search.
-   **`utilities/`** – `util.py` (YouTube info + ffmpeg helper), `logger.py`, `pydantic_models.py`.
-   **`database/`** – `models.py` (Song & SongFingerPrints), `database.py` (session + engine).
-   **`alembic/`** – Versioned SQL migrations (generated via `alembic revision --autogenerate`).

---

## Deployment Notes

-   Use **Gunicorn** with `uvicorn.workers.UvicornWorker` in production:
    ```bash
    uvicorn backend.main:APP
    ```
-   Persist the `downloaded_songs/` and `logs/` directories (bind-mount or volume).
-   Set `ECHO_SQL=False` in production.

---

## Troubleshooting

| Symptom                                        | Fix                                                                               |
| ---------------------------------------------- | --------------------------------------------------------------------------------- |
| `ffmpeg error: file not found`                 | Ensure FFmpeg is installed & on PATH.                                             |
| `All the environment variables are not set...` | Check `.env` keys; server will refuse to start if any are missing.                |
| No match found for obviously correct clip      | Experiment with `CONFIDENCE_THRESHOLD` or ensure DB has that song’s fingerprints. |

## Note

This is a personal project I created as a learning experiment to explore how real-world audio recognition tools like Shazam actually work. I've always been curious about how a short audio snippet can be converted into a unique fingerprint, matched against a database, and identified within seconds — and building this helped me understand those internal mechanics in much greater depth.

However, since this is still a work-in-progress and built for educational purposes, there are a few known limitations:

-   **🎧 Noise Sensitivity:** Songs recorded with background noise, echo, or overlapping audio may result in poor recognition accuracy.

-   **🔇 Low Volume:** Very quiet recordings may not generate enough strong peaks for meaningful fingerprinting.

-   **🎶 Limited Database:** Only a small number of songs are currently stored, so recognition works only for that subset.

-   **⚙️ No Machine Learning:** This system is entirely algorithm-based (no deep learning or neural networks), which means it might not be as robust as commercial tools in edge cases.

Despite these limitations, the Wizard can work well if short clips of songs—whose fingerprints are already available—are fed directly into it.
