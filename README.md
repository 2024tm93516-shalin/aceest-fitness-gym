# ACEest Fitness & Gym — DevOps Assignment (BITS WILP)

## Overview
REST API for gym client management built with Flask and SQLite, delivered through a
fully automated DevOps pipeline: Git → GitHub → GitHub Actions CI → Jenkins BUILD → Docker.

## Tech Stack
- **Application**: Python 3.11, Flask, SQLite
- **Testing**: Pytest
- **Containerisation**: Docker
- **CI Pipeline**: GitHub Actions
- **Build Server**: Jenkins
- **Version Control**: Git / GitHub

## Local Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/aceest-gym-v2.git
cd aceest-gym-v2

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the application
python app.py
# Runs at http://localhost:5000
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service health check |
| GET | `/programs` | List available fitness plans |
| POST | `/clients` | Register a new client |
| GET | `/clients/<name>` | Retrieve client profile |
| POST | `/clients/<name>/progress` | Record weekly adherence |
| GET | `/clients/<name>/bmi` | Compute BMI and category |

## Running Tests

```bash
pytest tests/ -v
```

## Docker Usage

```bash
# Build
docker build -t aceest-gym-app .

# Run
docker run -p 5000:5000 aceest-gym-app

# Test inside container
docker run --rm aceest-gym-app pytest tests/ -v
```

## GitHub Actions CI

Triggers on every push and pull request to `main`. Stages:
1. **Syntax Check** — validates `app.py` with `py_compile`
2. **Unit Tests** — runs full pytest suite
3. **Docker Build** — builds container image
4. **Container Tests** — reruns pytest inside the built image

Pipeline file: `.github/workflows/main.yml`

## Jenkins BUILD Pipeline

Pulls latest code from GitHub and runs:
1. **Source Checkout** — fetches from GitHub
2. **Snapshot Previous Build** — saves current image for rollback
3. **Syntax Check** — validates Python syntax
4. **Docker Build** — builds image tagged with `BUILD_NUMBER`
5. **Containerised Tests** — pytest inside Docker
6. **Promote to Latest** — tags image as `aceest-gym-app:latest`

On failure, automatically restores the previous image as `latest`.

Pipeline file: `Jenkinsfile`

### Jenkins Setup
1. Open Jenkins at `http://<bits-vm-ip>:8080`
2. New Item → Pipeline → name it `aceest-gym-app`
3. Pipeline script from SCM → Git
4. Repository URL → your GitHub repo URL
5. Branch → `*/main` | Script Path → `Jenkinsfile`
6. Save → Build Now

## Version History

| Tag | Description |
|-----|-------------|
| v1.0 | Initial Flask app with SQLite |
| v1.1 | Progress tracking endpoints added |
| v1.2 | BMI, metrics, workout logging — stable release |
