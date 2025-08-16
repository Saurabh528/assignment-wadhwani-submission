# AI-Driven Content Factory

## Overview
An intelligent content generation pipeline that transforms topics into structured educational videos with character-based narration and automated quality assurance.

## Features
- **Curriculum Generation**: Breaks topics into 3-5 structured lessons
- **Character Management**: Database-driven character library with voice profiles
- **Script Generation**: AI-powered script writing with character dialogues
- **TTS Integration**: Multi-voice text-to-speech with consistency checking
- **Video Assembly**: Automated scene generation with captions
- **Quality Assurance**: Automated checks for audio sync, character consistency, and caption alignment

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- FFmpeg installed
- API Keys for Groq, Together AI (optional)

### 2. Installation
```bash
# Clone repository
git clone <repository-url>
cd content-factory

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env
echo "TOGETHER_API_KEY=your_key_here" >> .env
```

### 3. Run Application
```bash
streamlit run app.py
```

## Architecture

### Agent-Based System
- **Curriculum Agent**: Generates structured lesson plans
- **Script Agent**: Creates character-based video scripts
- **QA Agent**: Performs quality checks and auto-corrections

### Core Modules
- **Character Manager**: SQLite-based character library
- **TTS Manager**: Voice generation with consistency
- **Video Generator**: Scene assembly and rendering

## Technology Stack
- **Frontend**: Streamlit 1.28.0
- **LLM**: Groq API (Llama 3.1)
- **TTS**: Edge-TTS 6.1.9
- **Video**: MoviePy 1.0.3
- **Database**: SQLite3
- **Image Processing**: Pillow 10.1.0

## Cost Estimation
### Per Video (60 seconds)
- LLM API: $0.002
- TTS Generation: $0.005
- Image Generation: $0.05
- Video Rendering: $0.05
- Storage: $0.002
- **Total**: ~$0.11 per minute

## Scalability Considerations
- Batch processing for multiple videos
- Caching for repeated characters
- CDN for video distribution
- Serverless architecture for rendering

## Demo Video
[Link to 15-20 minute walkthrough]