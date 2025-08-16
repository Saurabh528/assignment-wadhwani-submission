#!/usr/bin/env python3
"""
Test script for voice functionality
"""

import os
import sys
from core.tts_manager import TTSManager
from core.character_manager import CharacterManager

def test_voice_functionality():
    """Test the enhanced voice functionality"""
    
    print("🎤 Testing Voice Functionality")
    print("=" * 50)
    
    # Test TTS Manager
    print("\n1. Testing TTS Manager...")
    tts_manager = TTSManager()
    
    # Test voice styles
    voice_styles = tts_manager.get_voice_style_descriptions()
    print(f"✅ Available voice styles: {len(voice_styles)}")
    for style, desc in voice_styles.items():
        print(f"   • {style}: {desc}")
    
    # Test voice mapping
    print(f"\n✅ Voice mappings: {len(tts_manager.voice_mapping)} combinations")
    
    # Test voice characteristics
    voice_chars = tts_manager.get_voice_characteristics()
    print(f"✅ Voice characteristics: {len(voice_chars)} OpenAI voices")
    for voice, char in voice_chars.items():
        print(f"   • {voice}: {char}")
    
    # Test voice mapping info
    print("\n2. Testing voice mapping info...")
    test_combinations = [
        ("Male", "Professional"),
        ("Female", "Friendly"),
        ("Neutral", "Energetic"),
        ("Male", "Confident"),
        ("Female", "Playful")
    ]
    
    for gender, style in test_combinations:
        info = tts_manager.get_voice_mapping_info(gender, style)
        print(f"   • {gender} {style} → {info['mapped_voice']} ({info['characteristic']})")
    
    # Test character creation with voice styles
    print("\n3. Testing character creation with voice styles...")
    character_manager = CharacterManager(test_mode=True)
    
    test_characters = [
        {
            "name": "Test Professor",
            "description": "Professional educator with glasses",
            "voice_style": "Professional",
            "gender": "Male"
        },
        {
            "name": "Test Student",
            "description": "Curious learner",
            "voice_style": "Friendly",
            "gender": "Female"
        },
        {
            "name": "Test Narrator",
            "description": "Storytelling expert",
            "voice_style": "Narrative",
            "gender": "Neutral"
        }
    ]
    
    for char_data in test_characters:
        try:
            result = character_manager.add_character(char_data, generate_avatar=False)
            if result != -1:
                print(f"   ✅ Created character: {char_data['name']} ({char_data['voice_style']} {char_data['gender']})")
            else:
                print(f"   ⚠️ Character already exists: {char_data['name']}")
        except Exception as e:
            print(f"   ❌ Failed to create character {char_data['name']}: {str(e)}")
    
    # Test voice generation (if API key is available)
    print("\n4. Testing voice generation...")
    test_text = "Hello! This is a test of the voice synthesis system."
    
    for char_data in test_characters:
        try:
            # Get character from database
            char = character_manager.get_character(char_data['name'])
            if char:
                output_path = f"test_voice_{char_data['name'].replace(' ', '_')}.mp3"
                
                # Generate voice
                audio_path = tts_manager.generate_voiceover(
                    test_text,
                    {
                        "gender": char['gender'],
                        "voice_style": char['voice_style']
                    },
                    output_path
                )
                
                if os.path.exists(audio_path):
                    file_size = os.path.getsize(audio_path)
                    print(f"   ✅ Generated voice for {char_data['name']}: {audio_path} ({file_size} bytes)")
                else:
                    print(f"   ❌ Voice file not created for {char_data['name']}")
            else:
                print(f"   ⚠️ Character not found: {char_data['name']}")
                
        except Exception as e:
            print(f"   ❌ Voice generation failed for {char_data['name']}: {str(e)}")
    
    print("\n🎉 Voice functionality test completed!")
    print("\nTo test the dashboard:")
    print("1. Run: streamlit run app.py")
    print("2. Go to 'Step 2: Character Management'")
    print("3. Try creating characters with different voice styles")
    print("4. Use the voice preview and testing features")

if __name__ == "__main__":
    test_voice_functionality()
