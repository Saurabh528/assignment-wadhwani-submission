import os
import tempfile
from typing import Dict, List
from openai import OpenAI
from config import Config

class TTSManager:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        # Enhanced voice mapping with more voice styles
        self.voice_mapping = {
            # Professional voices
            "Male_Professional": "onyx",
            "Female_Professional": "nova",
            "Neutral_Professional": "alloy",
            
            # Friendly voices
            "Male_Friendly": "echo",
            "Female_Friendly": "shimmer",
            "Neutral_Friendly": "fable",
            
            # Energetic voices
            "Male_Energetic": "fable",
            "Female_Energetic": "alloy",
            "Neutral_Energetic": "echo",
            
            # Calm voices
            "Male_Calm": "onyx",
            "Female_Calm": "nova",
            "Neutral_Calm": "shimmer",
            
            # Confident voices
            "Male_Confident": "onyx",
            "Female_Confident": "nova",
            "Neutral_Confident": "alloy",
            
            # Playful voices
            "Male_Playful": "fable",
            "Female_Playful": "shimmer",
            "Neutral_Playful": "echo",
            
            # Narrative voices
            "Male_Narrative": "echo",
            "Female_Narrative": "nova",
            "Neutral_Narrative": "alloy",
            
            # Technical voices
            "Male_Technical": "onyx",
            "Female_Technical": "nova",
            "Neutral_Technical": "alloy"
        }
    
    def generate_voiceover(self, text: str, character: Dict, output_path: str) -> str:
        # Construct voice key
        voice_key = f"{character['gender']}_{character['voice_style']}"
        voice = self.voice_mapping.get(voice_key, "alloy")
        
        # Use OpenAI TTS for generation
        response = self.client.audio.speech.create(
            model=Config.TTS_MODEL,
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        # Save the audio content to file
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    
    def generate_batch_voiceovers(self, scenes: List[Dict]) -> List[str]:
        voiceover_paths = []
        
        for i, scene in enumerate(scenes):
            if 'dialogue' in scene and scene['dialogue']:
                temp_path = f"temp_audio_{i}.mp3"
                
                # Get character info
                character = {
                    'gender': scene.get('character_gender', 'Female'),
                    'voice_style': scene.get('voice_style', 'Professional')
                }
                
                self.generate_voiceover(
                    scene['dialogue'],
                    character,
                    temp_path
                )
                voiceover_paths.append(temp_path)
            else:
                voiceover_paths.append(None)
        
        return voiceover_paths
    
    def ensure_voice_consistency(self, character_name: str, scenes: List[Dict]) -> bool:
        character_voices = {}
        
        for scene in scenes:
            if scene.get('character') == character_name:
                voice_key = f"{scene.get('character_gender')}_{scene.get('voice_style')}"
                if character_name in character_voices:
                    if character_voices[character_name] != voice_key:
                        return False
                else:
                    character_voices[character_name] = voice_key
        
        return True
    
    def get_available_voices(self) -> Dict:
        return self.voice_mapping
    
    def get_openai_voices(self) -> List[str]:
        return Config.AVAILABLE_VOICES
    
    def get_voice_style_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all available voice styles"""
        return {
            "Professional": "Clear, authoritative voice suitable for educational content",
            "Friendly": "Warm, approachable voice that builds rapport",
            "Energetic": "Dynamic, enthusiastic voice that engages learners",
            "Calm": "Soothing, patient voice for complex topics",
            "Confident": "Self-assured, commanding presence",
            "Playful": "Fun, engaging voice for younger audiences",
            "Narrative": "Storytelling voice with natural flow",
            "Technical": "Precise, detailed voice for complex subjects"
        }
    
    def get_voice_characteristics(self) -> Dict[str, str]:
        """Get characteristics of OpenAI voices"""
        return {
            "onyx": "Deep, authoritative male voice",
            "nova": "Clear, professional female voice", 
            "echo": "Warm, friendly male voice",
            "shimmer": "Bright, engaging female voice",
            "fable": "Dynamic, expressive voice",
            "alloy": "Balanced, versatile voice"
        }
    
    def get_voice_mapping_info(self, gender: str, voice_style: str) -> Dict:
        """Get detailed information about a voice mapping"""
        voice_key = f"{gender}_{voice_style}"
        mapped_voice = self.voice_mapping.get(voice_key, "alloy")
        
        return {
            "voice_key": voice_key,
            "mapped_voice": mapped_voice,
            "gender": gender,
            "voice_style": voice_style,
            "description": self.get_voice_style_descriptions().get(voice_style, ""),
            "characteristic": self.get_voice_characteristics().get(mapped_voice, "")
        }