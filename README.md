# 🤖 Auto-Applicant Bot

## 🎯 Objective
This project aims to automate the tedious process of applying to Master's and PhD programs across various university portals. Instead of manually filling out the same personal, educational, and professional details hundreds of times, this bot acts as a "Co-Pilot" to:
*   **Navigate** application forms automatically.
*   **Fill** standard fields (Name, Address, GPA, etc.) from a central profile.
*   **Upload** documents (CV, Transcripts).
*   **Generate** custom essays using AI (Gemini) based on specific prompt questions.

## 🛠️ Tools & Tech Stack
*   **Python**: Core scripting language.
*   **Playwright**: Browser automation (headless Chrome).
*   **Docker**: Containerization to ensure it runs on any machine (Windows/Mac/Linux) without dependency hell.
*   **Google Gemini API**: LLM integration for generating context-aware essay responses.
*   **Streamlit**: (Feature) Web-based UI dashboard for easy control.
*   **GitHub Actions**: CI/CD pipeline to build and publish the Docker image.

## ⚙️ Process
1.  **Profile Setup**: You define your persona in `user_profile.json` (JSON) and place your documents (`cv.pdf`, etc.) in the folder.
2.  **Container Launch**: You run the Docker container with a target URL.
3.  **Automation Loop**:
    *   The bot launches a headless browser.
    *   It scans the page for inputs (text, radio, file uploads).
    *   It uses heuristics (and AI) to match your profile data to the form fields.
    *   It handles logins, navigates multi-page forms, and saves screenshots of its progress.
4.  **Review**: You check the `final_state.png` or HTML output to verify accuracy before final submission.

## 🚀 How to Test & Use

### Prerequisites
*   **Docker** installed and running.
*   **Gemini API Key** (optional, for AI essays).

### 1. Clone & Configure
```bash
git clone https://github.com/Abdul-Barri/auto-applicant-bot.git
cd auto-applicant-bot
```
*   Edit `user_profile.json` with your real details.
*   Replace `cv.pdf` and `transcript.pdf` with your actual files.

### 2. Run with Docker (Command Line)
To apply to a specific URL:
```bash
# Replace TARGET_URL with the university application link
# Replace YOUR_API_KEY with your Google Gemini Key
docker run --rm -v ${PWD}:/app -e GEMINI_API_KEY="YOUR_API_KEY" ghcr.io/abdul-barri/auto-applicant-bot:latest python apply.py "TARGET_URL"
```

### 3. Run with Dashboard (UI)
(Available on `feature/dashboard` branch)
```bash
docker run --rm -v ${PWD}:/app -p 8501:8501 ghcr.io/abdul-barri/auto-applicant-bot:latest streamlit run dashboard.py
```
Then open `http://localhost:8501` in your browser.

## 📦 Deployment
This project uses **GitHub Actions** for continuous deployment.
*   Every push to `master` automatically triggers a workflow.
*   The workflow builds the Docker image and publishes it to the **GitHub Container Registry (GHCR)**.
*   Users can always pull the latest stable version using `docker pull ghcr.io/abdul-barri/auto-applicant-bot:latest`.
