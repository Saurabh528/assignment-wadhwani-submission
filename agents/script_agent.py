from openai import OpenAI
import json
from core.character_manager import CharacterManager
from config import Config

class ScriptAgent:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL
        self.character_manager = CharacterManager()
    
    def generate(self, lesson, selected_character_names=None):
        # Get or create characters
        characters = []
        
        if selected_character_names:
            # Use selected characters
            for name in selected_character_names:
                char = self.character_manager.get_character(name)
                if char:
                    characters.append(char)
        
        # If no characters selected or found, use all available or create defaults
        if not characters:
            characters = self.character_manager.get_all_characters()
            if len(characters) < 2:
                # Create default characters if none exist
                self.character_manager.add_character({
                    "name": "Professor Alex",
                    "description": "Professional educator with glasses",
                    "voice_style": "Professional",
                    "gender": "Male"
                })
                self.character_manager.add_character({
                    "name": "Student Sam",
                    "description": "Curious learner",
                    "voice_style": "Friendly",
                    "gender": "Female"
                })
                characters = self.character_manager.get_all_characters()
        
        prompt = f"""
        Create a video script for this lesson:
        Title: {lesson['title']}
        Introduction: {lesson['introduction']}
        Main Body: {lesson['main_body']}
        Summary: {lesson['summary']}
        
        Use these characters:
        {json.dumps(characters[:2])}
        
        Requirements:
        - 4 to 8 scenes total
        - For each scene, craft the "visual" as a concise yet detailed image-generation prompt derived directly from the scene's dialogue so the image best depicts what is being said. Avoid including on-image text instructions. Use concrete nouns, setting, lighting, camera angle, mood, and style suitable for educational content.
        - Keep "duration" realistic for the spoken dialogue.
        
        Return as JSON with structure:
        {{
            "scenes": [
                {{
                    "scene_number": 1,
                    "duration": 5,
                    "visual": "A detailed image prompt derived from the dialogue",
                    "character": "Character name",
                    "dialogue": "What the character says",
                    "captions": "Text overlay if any"
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a video script writer. Always ensure the visual prompt illustrates the dialogue vividly and clearly."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)