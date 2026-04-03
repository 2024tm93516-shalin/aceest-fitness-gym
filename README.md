# ACEest Fitness & Gym — BITS WILP DevOps Project

## About This Project
This project implements a backend web service for managing gym members and their fitness journeys at ACEest Fitness & Gym. The application exposes a set of HTTP endpoints built using the Flask framework with SQLite as the data store. The entire delivery process is automated through a modern DevOps toolchain that takes code from a developer's machine all the way to a running container on a build server.

The pipeline follows this flow:
```
Local Development → Git Commits → GitHub → GitHub Actions → Jenkins → Docker Container
```

## Tools and Technologies

| Category | Technology |
|---|---|
| Language | Python 3.11 |
| Web Framework | Flask |
| Database | SQLite |
| Test Framework | Pytest |
| Containerisation | Docker |
| Automated CI | GitHub Actions |
| Build Automation | Jenkins |
| Source Control | Git and GitHub |

## Getting Started Locally

```bash
# 1. Get the code
git clone https://github.com/<your-username>/aceest-fitness-gym.git
cd aceest-fitness-gym

# 2. Create an isolated Python environment
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Launch the server
python app.py
# Server starts at http://localhost:5000
```

## Available Endpoints

| HTTP Method | Route | What It Does |
|-------------|-------|--------------|
| GET | `/` | Returns service name, version and health status |
| GET | `/programs` | Retrieves all available fitness plans |
| POST | `/clients` | Registers a new gym member |
| GET | `/clients/<name>` | Looks up a member's full profile |
| POST | `/clients/<name>/progress` | Logs a member's weekly workout adherence |
| GET | `/clients/<name>/bmi` | Calculates and returns BMI with health category |

## How to Run the Tests

Activate the virtual environment first, then:
```bash
pytest tests/ -v
```
All test cases are headless and safe to run in any CI environment without a display.

## Working with Docker

```bash
# Build the container image
docker build -t aceest-fitness-gym .

# Launch the container and expose port 5000
docker run -p 5000:5000 aceest-fitness-gym

# Execute the test suite directly inside the container
docker run --rm aceest-fitness-gym pytest tests/ -v
```

## Continuous Integration — GitHub Actions

Every time code is pushed or a pull request is raised against the `main` branch, the following automated stages execute in sequence:

1. **Pull source code** — checks out the latest commit from the repository
2. **Load application dependencies** — installs all packages from `requirements.txt`
3. **Verify application syntax** — uses `py_compile` to catch any syntax errors before building
4. **Run test suite** — executes all pytest cases and fails the pipeline if any test breaks
5. **Assemble Docker image** — packages the application into a portable container
6. **Validate tests inside container** — reruns the full test suite inside the built image to confirm container integrity

Workflow definition: `.github/workflows/main.yml`

## Build Automation — Jenkins Pipeline

Jenkins handles the primary build phase by pulling the latest code from GitHub and executing the following stages:

1. **Source Checkout** — retrieves the latest commit from the `main` branch
2. **Snapshot Previous Build** — preserves the currently running image as a fallback before attempting a new build
3. **Syntax Check** — confirms the Python source has no syntax issues
4. **Docker Build** — constructs a new image tagged with the Jenkins build number
5. **Containerised Tests** — runs the full pytest suite inside the freshly built container
6. **Promote to Latest** — if all tests pass, the new image is tagged as `aceest-fitness-gym:latest`

If any stage fails, Jenkins automatically restores the previously snapshotted image as `latest`, ensuring the last known working version stays live.

Pipeline definition: `Jenkinsfile`

### Configuring Jenkins

1. Navigate to `http://<bits-vm-ip>:8080` and log in
2. Click "New Item" → enter `aceest-fitness-gym` → select "Pipeline" → click OK
3. Under "Pipeline", set Definition to "Pipeline script from SCM"
4. Set SCM to "Git" and paste your GitHub repository URL
5. Set Branch Specifier to `*/main` and Script Path to `Jenkinsfile`
6. Click Save, then click "Build Now"

## Release History

| Version | Summary |
|---------|---------|
| v1.0 | Foundation — Flask app with SQLite database setup |
| v1.1 | Enhancement — weekly progress tracking added |
| v1.2 | Stable release — BMI calculator, body metrics and workout history |
