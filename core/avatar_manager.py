import os
import json
import requests
from openai import OpenAI
from config import Config
import hashlib
from typing import Dict, Optional

class AvatarManager:
    def __init__(self, test_mode=True):
        """
        Initialize Avatar Manager
        
        Args:
            test_mode (bool): If True, uses low quality for cost savings during testing
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.test_mode = test_mode
        self.avatar_dir = os.path.join(Config.OUTPUT_DIR, "avatars")
        os.makedirs(self.avatar_dir, exist_ok=True)
        
    def get_image_quality(self):
        """Get image quality based on test mode"""
        return Config.IMAGE_QUALITY if self.test_mode else Config.IMAGE_QUALITY_PRODUCTION
    
    def generate_avatar_prompt(self, character_details: Dict) -> str:
        """
        Generate a detailed prompt for avatar creation
        
        Args:
            character_details: Dictionary containing character information
            
        Returns:
            Formatted prompt for DALL-E 3
        """
        # Get character attributes
        gender = character_details.get('gender', 'person')
        description = character_details.get('description', '')
        voice_style = character_details.get('voice_style', 'Professional')
        
        # Build dynamic prompt based on available information
        base_prompt = f"Professional portrait photograph of a {gender}"
        
        # Add role based on voice style
        if voice_style.lower() == 'professional':
            base_prompt += " educator or professor"
        elif voice_style.lower() == 'friendly':
            base_prompt += " teacher or mentor"
        elif voice_style.lower() == 'energetic':
            base_prompt += " motivational speaker or coach"
        elif voice_style.lower() == 'calm':
            base_prompt += " counselor or guide"
        else:
            base_prompt += " instructor"
        
        # If description is provided, use it; otherwise generate based on attributes
        if description and len(description) > 10:
            appearance = description
        else:
            # Generate generic but appropriate appearance
            if gender.lower() == 'male':
                appearance = "Well-groomed man with professional attire"
            elif gender.lower() == 'female':
                appearance = "Well-presented woman with professional attire"
            else:
                appearance = "Well-dressed person with professional appearance"
        
        prompt = f"""{base_prompt}

Appearance: {appearance}
Expression: {voice_style.lower()} and approachable demeanor, warm smile, direct eye contact

Technical specifications:
- Front-facing portrait, shoulders and head visible
- Centered in frame
- Professional studio lighting
- Clean, neutral background (light gray or soft gradient)
- Photorealistic style
- High detail facial features for animation
- Natural skin tones
- No text or watermarks
- No accessories blocking face"""

        return prompt
    
    def generate_avatar(self, character_name: str, character_details: Dict, force_regenerate: bool = False) -> str:
        """
        Generate or retrieve avatar for a character
        
        Args:
            character_name: Name of the character
            character_details: Character attributes
            force_regenerate: Force new generation even if avatar exists
            
        Returns:
            Path to the generated avatar image
        """
        # Create unique filename based on character name
        avatar_filename = f"{character_name.lower().replace(' ', '_')}_avatar.png"
        avatar_path = os.path.join(self.avatar_dir, avatar_filename)
        
        # Check if avatar already exists
        if os.path.exists(avatar_path) and not force_regenerate:
            print(f"Using existing avatar for {character_name}: {avatar_path}")
            return avatar_path
        
        try:
            # Generate prompt
            prompt = self.generate_avatar_prompt(character_details)
            
            # Generate image using DALL-E 3
            response = self.client.images.generate(
                model=Config.IMAGE_MODEL,
                prompt=prompt,
                size=Config.IMAGE_SIZE,
                quality=self.get_image_quality(),
                n=1
            )
            
            # Download and save the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                with open(avatar_path, 'wb') as f:
                    f.write(image_response.content)
                print(f"Avatar generated for {character_name}: {avatar_path}")
                print(f"Quality used: {self.get_image_quality()} (Test mode: {self.test_mode})")
                return avatar_path
            else:
                raise Exception(f"Failed to download image: {image_response.status_code}")
                
        except Exception as e:
            print(f"Error generating avatar for {character_name}: {str(e)}")
            # Return a placeholder path for testing
            return self.create_placeholder_avatar(character_name)
    
    def create_placeholder_avatar(self, character_name: str) -> str:
        """
        Create a placeholder avatar for testing when API fails
        
        Args:
            character_name: Name of the character
            
        Returns:
            Path to placeholder image
        """
        placeholder_path = os.path.join(self.avatar_dir, f"{character_name.lower().replace(' ', '_')}_placeholder.png")
        
        # Create a simple placeholder image using PIL if available
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple avatar placeholder
            img = Image.new('RGB', (512, 512), color='lightgray')
            draw = ImageDraw.Draw(img)
            
            # Add initials
            initials = ''.join([word[0].upper() for word in character_name.split()[:2]])
            
            # Try to use a font, fall back to default if not available
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
            except:
                font = ImageFont.load_default()
            
            # Draw initials in center
            text_bbox = draw.textbbox((0, 0), initials, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            position = ((512 - text_width) / 2, (512 - text_height) / 2)
            draw.text(position, initials, fill='darkgray', font=font)
            
            img.save(placeholder_path)
            print(f"Created placeholder avatar for {character_name}")
            
        except ImportError:
            print("PIL not available, using dummy avatar path")
            placeholder_path = "dummy_avatar.png"
            
        return placeholder_path
    
    def get_avatar_path(self, character_name: str) -> Optional[str]:
        """
        Get the path to an existing avatar
        
        Args:
            character_name: Name of the character
            
        Returns:
            Path to avatar if exists, None otherwise
        """
        avatar_filename = f"{character_name.lower().replace(' ', '_')}_avatar.png"
        avatar_path = os.path.join(self.avatar_dir, avatar_filename)
        
        if os.path.exists(avatar_path):
            return avatar_path
        return None