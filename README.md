# AI-Based Personalised Exercise Coaching System

This project is an AI-powered exercise coaching system developed using Python, Streamlit, MediaPipe, and OpenCV. It provides personalised exercise guidance based on each user's mobility assessment and delivers real-time feedback using pose estimation.

---

## Using the System Online

Open the following URL in your web browser:

**https://exercise-coach-fyp.streamlit.app/**

---

## Downloading the Source Code and Running Locally

### Prerequisites

Before running the project, ensure the following are installed:

- Python 3.10 or later
- Git

---

### Installation Guide

#### Step 1: Download the Source Code

Click **Code → Download ZIP** on GitHub and extract the project.

---

#### Step 2: Open the Project

Open the project folder using **Visual Studio Code**.

---

#### Step 3: Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

#### Step 4: Install the Required Packages

```bash
pip install -r requirements.txt
```

---

#### Step 5: Run the Application

```bash
streamlit run main.py
```

After a few seconds, Streamlit will display a local address similar to:

```text
http://localhost:8501
```

Open this address in your web browser.

---

## Using the System

1. Register a new account.
2. Log in using your registered credentials.
3. Complete your user profile.
4. Perform the Mobility Assessment.
5. Review your personalised exercise recommendations.
6. Start a Live Exercise Session.
7. View your exercise history and progress.

---

## Notes

- Allow webcam permission when prompted.
- Use the system in a well-lit environment for optimal pose detection.
- The first launch may take longer while MediaPipe downloads the required model.
- Ensure your full body is visible within the camera frame during exercise sessions.
