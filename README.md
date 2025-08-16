# AI-Driven Content Factory

## Overview
An intelligent content generation pipeline that transforms topics into structured educational videos with character-based narration and automated quality assurance.

## Features
- **Curriculum Generation**: Breaks topics into 3-5 structured lessons
- **Character Management**: Database-driven character library with voice profiles
- **Script Generation**: AI-powered script writing with character dialogues
- **TTS Integration**: Multi-voice text-to-speech with consistency checking
- **Video Assembly**: Automated scene generation with captions

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- FFmpeg installed
- API Keys for OPENAI

### 2. Installation
```bash
# Clone repository
git clone <repository-url>
cd assignment-wadhwani-submission

# Install dependencies
pip install -r requirements.txt

# Create .env file
enter open ai api
```

### 3. Run Application
```bash
streamlit run app.py
```

## Architecture

### Agent-Based System
- **Curriculum Agent**: Generates structured lesson plans
- **Script Agent**: Creates character-based video scripts
- **QA Agent**: Performs quality checks and auto-corrections (to be implemented)

### Core Modules
- **Character Manager**: SQLite-based character library
- **TTS Manager**: Voice generation with consistency
- **Video Generator**: Scene assembly and rendering

## Technology Stack
- **Frontend**: Streamlit 1.28.0
- **LLM**: OpenAI API (Llama 3.1)
- **TTS**: Edge-TTS 6.1.9
- **Video**: MoviePy 1.0.3
- **Database**: SQLite3
- **Image Processing**: Pillow 10.1.0




