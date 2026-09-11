# Captik

### AI-Powered Video Captioning Studio

**Automatically generate beautiful, kinetic-style captions for your videos using Whisper + FFmpeg.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.1-green?logo=django&logoColor=white)](https://djangoproject.com)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-black?logo=openai)](https://github.com/openai/whisper)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Caption%20Burning-orange)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-Private-red)]()

---

## What is Captik?

**Captik** is a full-stack Django application that turns any video into a professionally captioned video in minutes.

It combines:
- **OpenAI Whisper** → Accurate word-level transcription
- **Custom ASS subtitle engine** → Beautiful kinetic / neon / fire / podcast styles
- **Google Fonts support** → Pick any font you want
- **FFmpeg burning** → Hardcoded captions into the final video

Perfect for content creators, YouTubers, TikTok editors, and agencies who want high-quality auto-captions without expensive tools.

---

## Features

- Upload any video → Get captioned version automatically
- **7 Caption Styles**:
  - Clean / Classic
  - Neon Glow
  - Fire Animation
  - Emboss Style
  - Gradient Split
  - Pill Badge
  - Podcast Stack
- Live font search (Google Fonts)
- Word-level timestamps for precise timing
- User system with Free / Pro plans
- Dashboard to manage all projects
- Background processing ready (Celery support)

---

## Tech Stack

| Layer              | Technology                  |
|--------------------|-----------------------------|
| Backend            | Django 6.1 + Django REST    |
| Transcription      | OpenAI Whisper (base model) |
| Caption Rendering  | Custom ASS + FFmpeg         |
| Fonts              | Google Fonts (auto download)|
| Task Queue         | Celery (memory broker)      |
| Database           | SQLite (easy to switch)     |

---

## Project Structure

```
Captik/
├── captik_core/          # Django project settings
├── caption_app/          # Main application
│   ├── models.py         # VideoProject, CaptionTemplate, UserProfile
│   ├── services/
│   │   ├── caption_pipeline.py   # Core transcription + burning logic
│   │   ├── font_engine.py
│   │   └── google_font_downloader.py
│   ├── templates/        # Dashboard UI
│   └── management/       # Custom commands
├── media/                # Uploaded & output videos
└── manage.py
```

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/ahmadraza-automation/Captik.git
cd Captik

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install django openai-whisper ffmpeg-python

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

> **Note:** You also need `ffmpeg` installed on your system.

---

## How It Works

1. User uploads a video from the dashboard
2. Selects a caption style + optional Google Font
3. Whisper transcribes the video with word timestamps
4. Captik groups words into short punchy chunks
5. Generates a styled `.ass` subtitle file
6. FFmpeg burns the captions into the video
7. Final captioned video is ready for download

---

## Author

**Ahmad Raza**  
Python Developer | Automation Engineer | AI Tools Builder  

- GitHub: [ahmadraza-automation](https://github.com/ahmadraza-automation)
- Email: arjafri347@gmail.com

---

<div align="center">

**Made with focus on speed & quality**

</div>
