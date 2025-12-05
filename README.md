# 🎵 Music Wizard – Full-Stack Audio Fingerprinting App

Music Wizard is an **open-source monorepo** that stores songs, fingerprints them, and later recognises short audio clips – think Shazam, but DIY. [Live Here](https://musicwizard.myddns.me/)

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

-   **API:** FastAPI · SQLAlchemy · Alembic · Pydantic · Uvicorn  
    Audio analysis via **Librosa**, **NumPy**, **SciPy**.  
    YouTube → MP3 conversion through a RapidAPI endpoint.
-   **DB:** SQLite for local dev, Postgres in production.
-   **Client:** React 18 · TypeScript · Vite (optionally Tailwind CSS).
-   **Deployment:** Full Docker containerization with multi-stage builds for both frontend and backend.
-   **Infra:** `.env` for configuration, GitHub Actions planned for CI.

---

## 🚀 Quick Start (Recommended: Docker)

### 🐳 Docker Deployment (Recommended)

Alternatively, you can run each service separately:

```bash
# 1. Clone and configure
git clone https://github.com/Prithvi824/Muisc-Wizard.git
cd Muisc-Wizard
cp .env.example .env
# Edit .env with your credentials

# 2. Build and run backend
cd backend
docker build -t music-wizard-backend .
docker run -d -p 8000:8000 --env-file ../.env music-wizard-backend

# 3. Build and run frontend (in a new terminal)
cd ../frontend
docker build -t music-wizard-frontend .
docker run -d -p 3000:80 music-wizard-frontend
```

**Benefits of Docker deployment:**

-   ✅ No need to install Node.js or Python dependencies locally
-   ✅ Consistent environment across different systems
-   ✅ Production-ready with Nginx (frontend) and Gunicorn (backend)
-   ✅ Minimal attack surface with optimized runtime images
-   ✅ Easy to scale and deploy

### 📋 Manual Installation (Alternative)

<details>
<summary>Click to expand manual installation steps</summary>

> ⚠️ **Note:** Docker deployment is recommended for better consistency and easier setup.

```bash
# 1. Clone & create env
git clone https://github.com/Prithvi824/Muisc-Wizard.git
cd Muisc-Wizard

# Create virtual environment (recommended)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Configure secrets
# Copy .env.example → .env and fill in the keys
# ⚠️ FFmpeg must be installed and available on your PATH

# 3. Start the backend
pip install -r backend/requirements.txt      # install python deps
alembic -c backend/alembic.ini upgrade head  # migrate database
uvicorn backend.main:APP --reload            # http://localhost:8000/docs

# 4. Start the frontend (new terminal)
cd frontend
npm install   # or pnpm / yarn
npm run dev   # http://localhost:5173
```

</details>

### 🎯 Getting Started

Once your services are running:

1. **Add songs**: Visit `http://localhost:8000/docs` and use `GET /add-song?yt_url=<youtube_url>` to load songs into the database
2. **Test recognition**: Open `http://localhost:3000` (Docker) or `http://localhost:5173` (dev), record or upload a short audio clip, and see the magic happen!

> **Docker users**: Frontend runs on port 3000 and automatically connects to the backend API.  
> **Dev users**: Frontend dev server on port 5173 proxies API requests to `localhost:8000`.

---

## 🔑 Environment Variables

> **Docker Users:** These variables should be set in your `.env` file when using `--env-file .env` with Docker.

| Variable                    | Example                            | Description                             |
| --------------------------- | ---------------------------------- | --------------------------------------- |
| `DB_STRING`                 | `sqlite:///wizard.db`              | SQLAlchemy URI (use Postgres in prod)   |
| `ECHO_SQL`                  | `True`                             | Log SQL (debug only)                    |
| `YT_TO_MP3_URL`             | `https://yt-mp3.p.rapidapi.com/dl` | RapidAPI endpoint                       |
| `QUERY_PARAM_YT_TO_MP3_URL` | `id`                               | Query-string key for above              |
| `RAPID_API_KEY`             | _secret_                           | RapidAPI key                            |
| `RAPID_API_HOST`            | _secret_                           | RapidAPI host header                    |
| `SONG_DIR`                  | `downloaded_songs`                 | Where MP3s are cached                   |
| `SAMPLE_RATE`               | `44100`                            | Audio resample rate                     |
| `CONFIDENCE_THRESHOLD`      | `0.3`                              | Minimum score for a match               |
| `VITE_API_URL`              | `http://localhost:8000`            | Frontend fetches API from this base URL |

---

## 🔍 Common Commands

### Docker Commands

```bash
# Docker builds
docker build -t music-wizard-backend ./backend
docker build -t music-wizard-frontend ./frontend

# Run backend with persistent volumes
docker run -d -p 8000:8000 --env-file .env \
  -v $(pwd)/downloaded_songs:/app/downloaded_songs \
  -v $(pwd)/logs:/app/logs \
  music-wizard-backend

# Run frontend
docker run -d -p 3000:80 music-wizard-frontend

# Container management
docker logs <container_id>         # View logs
docker stop <container_id>         # Stop container
docker system prune -f             # Clean up unused containers/images
```

### Development Commands

```bash
# Frontend development
cd frontend && npm run dev

# Backend API documentation
# Visit http://localhost:8000/docs (when backend is running)

# Generate new Alembic migration (manual setup only)
alembic revision --autogenerate -m "description"

# Code quality
ruff format . && ruff check .

# Frontend unit tests
npm test
```

---

## 🧩 Further Reading

-   Backend internals & API reference → `backend/README.md`
-   Frontend tooling & scripts → `frontend/README.md`
-   Research notes & papers → `research/`

---

## 🤝 Contributing

1. Fork & create a feature branch.
2. Keep commits small & focused; add tests where possible.
3. Run `pre-commit run -a` before pushing.
4. Submit a PR – feedback welcome!

---

## 📝 License

Released under the **MIT License**. See `LICENSE` for details.
