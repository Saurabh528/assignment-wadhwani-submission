"""
OpenAI TTS Manager for custom speech synthesis with instructions
Separate from the existing TTS system for specialized use cases
"""

import os
import requests
from typing import Dict, Optional
from openai import OpenAI
from config import Config
import hashlib

class OpenAITTSManager:
    def __init__(self):
        """
        Initialize OpenAI TTS Manager for custom speech synthesis
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.output_dir = os.path.join(Config.OUTPUT_DIR, "openai_speech")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Available voices for OpenAI TTS
        self.available_voices = [
            "alloy", "echo", "fable", "onyx", "nova", "shimmer"
        ]
        
        # Available models
        self.available_models = ["tts-1", "tts-1-hd"]
    
    def generate_speech_with_instructions(
        self,
        text: str,
        instructions: str = "Speak in a natural and clear voice.",
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate speech using OpenAI TTS with custom instructions
        
        Args:
            text: Text to synthesize
            instructions: Voice instructions (e.g., "Speak in a cheerful and positive tone.")
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: Model to use (tts-1 or tts-1-hd)
            speed: Speech speed (0.25 to 4.0)
            output_filename: Custom filename, auto-generated if None
            
        Returns:
            Path to the generated audio file
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        if voice not in self.available_voices:
            raise ValueError(f"Voice must be one of: {', '.join(self.available_voices)}")
        
        if model not in self.available_models:
            raise ValueError(f"Model must be one of: {', '.join(self.available_models)}")
        
        if not (0.25 <= speed <= 4.0):
            raise ValueError("Speed must be between 0.25 and 4.0")
        
        # Generate filename if not provided
        if not output_filename:
            # Create a hash based on text, instructions, and voice for uniqueness
            content_hash = hashlib.md5(
                f"{text}_{instructions}_{voice}_{model}_{speed}".encode()
            ).hexdigest()[:8]
            output_filename = f"openai_speech_{content_hash}.mp3"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Check if file already exists
        if os.path.exists(output_path):
            print(f"Using existing audio file: {output_path}")
            return output_path
        
        try:
            # Combine instructions with text for better voice control
            # Note: OpenAI TTS doesn't have a direct instructions parameter,
            # but we can embed instructions in the text for better results
            enhanced_text = f"[Voice instructions: {instructions}] {text}"
            
            print(f"Generating speech with OpenAI TTS...")
            print(f"Voice: {voice}, Model: {model}, Speed: {speed}")
            print(f"Instructions: {instructions}")
            
            # Generate speech using OpenAI TTS
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=enhanced_text,
                speed=speed
            )
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Speech generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            raise
    
    def generate_speech_simple(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Simple speech generation without custom instructions
        
        Args:
            text: Text to synthesize
            voice: Voice to use
            model: Model to use
            output_filename: Custom filename
            
        Returns:
            Path to the generated audio file
        """
        return self.generate_speech_with_instructions(
            text=text,
            instructions="Speak in a natural and clear voice.",
            voice=voice,
            model=model,
            output_filename=output_filename
        )
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        return self.available_voices.copy()
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        return self.available_models.copy()
    
    def validate_parameters(
        self,
        voice: str,
        model: str,
        speed: float
    ) -> Dict[str, bool]:
        """
        Validate TTS parameters
        
        Returns:
            Dictionary with validation results
        """
        return {
            "voice_valid": voice in self.available_voices,
            "model_valid": model in self.available_models,
            "speed_valid": 0.25 <= speed <= 4.0
        }
    
    def preview_voice_instructions(self, instructions: str) -> str:
        """
        Generate a preview text showing how instructions would be applied
        
        Args:
            instructions: Voice instructions
            
        Returns:
            Preview text
        """
        sample_text = "Hello! This is a preview of how your voice instructions will sound."
        return f"[Voice instructions: {instructions}] {sample_text}"
    
    def get_speech_info(self, audio_path: str) -> Optional[Dict]:
        """
        Get information about a generated speech file
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        if not os.path.exists(audio_path):
            return None
        
        file_size = os.path.getsize(audio_path)
        file_name = os.path.basename(audio_path)
        
        return {
            "path": audio_path,
            "filename": file_name,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "exists": True
        }
