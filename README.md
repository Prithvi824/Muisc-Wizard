# 🎵 Music Wizard – Full-Stack Audio Fingerprinting App

Music Wizard is an **open-source monorepo** that stores songs, fingerprints them, and later recognises short audio clips – think Shazam, but DIY.

It comprises:

1. **Backend** – Python FastAPI service for downloading, fingerprinting, matching and persisting songs.
2. **Frontend** – React + Vite + TypeScript SPA for recording / uploading clips and showing match results.

> **Status:** Hobby / learning project – still evolving. Ideas & PRs welcome!

---

## 🗺️ Repository Layout
```
wizard.io/
├── backend/            # FastAPI service  ➜  backend/README.md
├── frontend/           # React client     ➜  frontend/README.md
├── downloaded_songs/   # Cached original MP3s (runtime-generated)
├── change_full_chunks/ # Experiments & scratch code
├── logs/               # Application & fingerprinting logs
├── .env*               # Runtime secrets (NOT committed)
└── README.md           # ← you are here
```

## ⚙️ Tech Stack
* **API:** FastAPI · SQLAlchemy · Alembic · Pydantic · Uvicorn  
  Audio analysis via **Librosa**, **NumPy**, **SciPy**.  
  YouTube → MP3 conversion through a RapidAPI endpoint.
* **DB:** SQLite for local dev, Postgres in production.
* **Client:** React 18 · TypeScript · Vite (optionally Tailwind CSS).
* **Infra:** `.env` for configuration, GitHub Actions planned for CI, Docker-compose template WIP.

---

## 🚀 Quick Start
### 1. Clone & create env
```bash
git clone https://github.com/your-user/music-wizard.git
cd music-wizard/wizard.io

# optional but recommended
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Configure secrets
Copy `.env.example` ➜ `.env` at the repo root and fill in the keys (see table below).  
⚠️ FFmpeg must be installed and available on your PATH.

### 3. Start the backend
```bash
pip install -r backend/requirements.txt      # install python deps
alembic -c backend/alembic.ini upgrade head  # migrate database
uvicorn backend.main:APP --reload            # http://localhost:8000/docs
```

### 4. Start the frontend (new terminal)
```bash
cd frontend
npm install   # or pnpm / yarn
npm run dev   # http://localhost:5173
```
Now you can:
1. `GET /add-song?yt_url=<youtube_url>` to load a song into the DB.  
2. Record / upload a short clip from the UI → it hits `POST /match-audio` and displays matches.

> Frontend dev server proxies API requests to `localhost:8000`, so CORS just works.

---

## 🔑 Environment Variables
Variable | Example | Description
---------|---------|------------
`DB_STRING` | `sqlite:///wizard.db` | SQLAlchemy URI (use Postgres in prod)
`ECHO_SQL` | `True` | Log SQL (debug only)
`YT_TO_MP3_URL` | `https://yt-mp3.p.rapidapi.com/dl` | RapidAPI endpoint
`QUERY_PARAM_YT_TO_MP3_URL` | `id` | Query-string key for above
`RAPID_API_KEY` | _secret_ | RapidAPI key
`RAPID_API_HOST`| _secret_ | RapidAPI host header
`SONG_DIR` | `downloaded_songs` | Where MP3s are cached
`SAMPLE_RATE` | `44100` | Audio resample rate
`CONFIDENCE_THRESHOLD` | `0.3` | Minimum score for a match
`VITE_API_URL` | `http://localhost:8000` | Frontend fetches API from this base URL

---

## 🔍 Common Commands
```bash
# Run backend tests (when added)
pytest

# Generate new Alembic migration
authoring="add-column" && alembic revision --autogenerate -m "$authoring"

# Code quality
ruff format . && ruff check .

# Frontend unit tests
npm test
```

---

## 🧩 Further Reading
* Backend internals & API reference → `backend/README.md`
* Frontend tooling & scripts → `frontend/README.md`
* Research notes & papers → `research/`

---

## 🤝 Contributing
1. Fork & create a feature branch.  
2. Keep commits small & focused; add tests where possible.  
3. Run `pre-commit run -a` before pushing.  
4. Submit a PR – feedback welcome!

---

## 📝 License
Released under the **MIT License**. See `LICENSE` for details.
