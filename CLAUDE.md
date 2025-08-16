# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Driven Content Factory - A Streamlit application that transforms topics into structured educational videos with character-based narration and automated quality assurance. The system uses OpenAI's GPT models for content generation and provides avatar-based video creation with optional lip-sync capabilities.

## Architecture

### Agent-Based System
- **CurriculumAgent** (`agents/curriculum_agent.py`): Generates structured lesson plans from topics using OpenAI API
- **ScriptAgent** (`agents/script_agent.py`): Creates character-based video scripts from lessons
- **QAAgent** (`agents/qa_agent.py`): Performs quality checks and auto-corrections

### Core Modules
- **CharacterManager** (`core/character_manager.py`): SQLite-based character library with avatar support
- **AvatarManager** (`core/avatar_manager.py`): Handles avatar image generation using DALL-E
- **TTSManager** (`core/tts_manager.py`): Voice generation with consistency checking
- **AvatarVideoGenerator** (`core/avatar_video_generator.py`): Creates split-screen educational videos with avatars
- **SadTalkerManager** (`core/sadtalker_manager.py`): Optional lip-sync integration

### Configuration
- **Config** (`config.py`): Central configuration including API keys, model settings, and cost estimation
- **Environment Variables**: Store in `.env` file (OPENAI_API_KEY required)

## Common Commands

### Setup and Installation
```bash
# Quick setup (recommended for testing - static avatars only)
make quick-start

# Full setup with lip-sync capabilities
make full-setup

# Manual dependency installation
python3 install_dependencies.py

# Install SadTalker (optional, for lip-sync)
python3 setup_sadtalker.py
```

### Development
```bash
# Run the application
make run
# or directly:
streamlit run app.py

# Run tests
make test

# Quick test of core functionality
make quick-test

# Clean temporary files
make clean

# Show system information
make info
```

### Testing and Verification
```bash
# Comprehensive system check
python3 check_system.py

# Test core modules
python3 -c "from core.character_manager import CharacterManager; print('✅ Works')"

# Check PyTorch installation (for SadTalker)
python3 -c "import torch; print(torch.__version__)"
```

## Key Implementation Notes

### Video Generation Modes
1. **Static Avatar Mode**: Fast generation with static character images
   - Enable: "Generate AI Avatars" + "Avatar-Based Videos"
   - Disable: "SadTalker Lip-Sync"

2. **Lip-Sync Mode**: Realistic lip-synchronized avatars (requires SadTalker)
   - Enable all three avatar options

### Database Structure
- SQLite database: `characters.db`
- Characters table includes: name, description, voice_style, gender, avatar_path, usage_count

### Test Assets
- Dummy assets in `dummy_assets/` directory for cost-free testing
- Enable "Use test assets" checkbox in sidebar to bypass API calls
- Pre-generated lessons stored in `dummy_assets/lessons.json`

### API Integration
- Uses OpenAI's GPT-4.1-mini for text generation
- DALL-E 3 for avatar image generation
- TTS-1 for voice synthesis
- Test mode uses low quality settings to reduce costs

### Platform Optimization
- Auto-detects Apple Silicon vs Intel Mac
- Uses MPS (Metal Performance Shaders) on M1/M2/M3 chips
- Falls back to CPU on Intel Macs

## Important Considerations

### Cost Management
- Image generation: Use test_mode=True for low quality during development
- Enable "Use test assets" to avoid API calls entirely
- Cost estimation available in Config.estimate_cost()

### Error Handling
- Character names must be unique (enforced at database level)
- Scripts require at least one character selected
- Video generation validates scene data before processing

### Performance
- Apple Silicon (M1/M2/M3): ~30-90s per video
- Intel Mac: ~90-120s per video
- Memory usage: 4-8GB typical

### Session State Management
- Streamlit session state stores:
  - `curriculum`: Generated lesson plans
  - `scripts`: Generated video scripts per lesson
  - `selected_characters`: Characters chosen for scripts
  - `videos`: Generated video paths