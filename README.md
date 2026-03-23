# 🎬 video-dubber-v4

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenAI Whisper](https://img.shields.io/badge/Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **AI-powered video dubbing system that transcribes, translates, and re-voices video content into Kannada using Whisper, gTTS, and MoviePy.**

---

## ✨ Features

- 🎙️ **Auto Transcription** — Extracts speech from any video using OpenAI Whisper
- 🌐 **AI Translation** — Translates English audio to Kannada using deep-translator
- 🔊 **Voice Synthesis** — Generates natural Kannada speech using Google Text-to-Speech (gTTS)
- 🎞️ **Video Merging** — Seamlessly merges the dubbed audio back into the original video with MoviePy
- 🔐 **User Authentication** — Secure login system with session management
- 🖥️ **Streamlit UI** — Clean, easy-to-use web interface — no CLI required

---

## 🏗️ Architecture

```
video-dubber-v4/
│
├── app.py                  # Streamlit web app entry point
├── requirements.txt        # Python dependencies
│
└── pipeline/
    ├── __init__.py
    ├── auth.py             # User authentication & session management
    ├── extractor.py        # Audio extraction from video
    ├── transcriber.py      # Speech-to-text using Whisper
    ├── translator.py       # English → Kannada translation
    ├── synthesizer.py      # Text-to-speech (Kannada) using gTTS
    ├── merger.py           # Dubbed audio + original video merging
    └── lipsync.py          # Lip-sync processing
```

### Pipeline Flow

```
Video Input
    ↓
[extractor.py]   →   Extract audio
    ↓
[transcriber.py] →   Whisper: Audio → English text
    ↓
[translator.py]  →   deep-translator: English → ಕನ್ನಡ
    ↓
[synthesizer.py] →   gTTS: Kannada text → Kannada audio
    ↓
[merger.py]      →   MoviePy: Merge audio + video
    ↓
Dubbed Video Output 🎬
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.9+
- FFmpeg installed on your system

**Install FFmpeg (macOS):**
```bash
brew install ffmpeg
```

**Install FFmpeg (Ubuntu/Debian):**
```bash
sudo apt install ffmpeg
```

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/kuvaleshcd-hue/video-dubber-v4-.git
cd video-dubber-v4-

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Usage

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501` and:

1. **Login / Register** your account
2. **Upload** your video file
3. Click **"Dub to Kannada"**
4. **Download** the dubbed video

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Speech Recognition | [OpenAI Whisper](https://github.com/openai/whisper) |
| Translation | [deep-translator](https://github.com/nidhaloff/deep-translator) |
| Text-to-Speech | [gTTS (Google TTS)](https://gtts.readthedocs.io/) |
| Video Processing | [MoviePy](https://zulko.github.io/moviepy/) |
| Web Interface | [Streamlit](https://streamlit.io/) |
| Language | Python 3.9+ |

---

## 📋 Requirements

See [`requirements.txt`](requirements.txt) for the full list of dependencies.

---

## 🌟 Use Cases

- Dub English YouTube videos into Kannada
- Make educational content accessible to Kannada speakers
- Regional language localization for short films and demos

---

## 👨‍💻 Author

**Kuvalesh** — [@kuvaleshcd-hue](https://github.com/kuvaleshcd-hue)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
