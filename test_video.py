#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.video_generator import VideoGenerator
from core.tts_manager import TTSManager

async def test_video_generation():
    """Test video generation with a simple case"""
    
    print("Starting video generation test...")
    
    # Simple test script
    test_script = {
        "scenes": [
            {
                "scene_number": 1,
                "duration": 3,
                "visual": "A simple educational diagram showing the concept of machine learning",
                "character": "Teacher",
                "dialogue": "Welcome to machine learning basics.",
                "captions": "Machine Learning Basics"
            }
        ]
    }
    
    try:
        # Test TTS generation first
        print("Testing TTS generation...")
        tts_manager = TTSManager()
        
        # Test generating a single voiceover
        test_text = "Welcome to machine learning basics."
        test_character = {"gender": "Female", "voice_style": "Professional"}
        
        audio_path = await tts_manager.generate_voiceover(
            test_text, 
            test_character, 
            "test_audio.mp3"
        )
        print(f"TTS generated successfully: {audio_path}")
        
        # Test video generation
        print("Testing video generation...")
        video_generator = VideoGenerator()
        
        video_path = await video_generator.create_video(test_script, 3)
        print(f"Video generated successfully: {video_path}")
        
        # Check if files exist
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            print(f"Video file size: {file_size} bytes")
            return True
        else:
            print("Video file was not created")
            return False
            
    except Exception as e:
        print(f"Error during video generation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_video_generation())
    if success:
        print("✅ Video generation test passed!")
    else:
        print("❌ Video generation test failed!")