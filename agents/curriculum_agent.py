from openai import OpenAI
import json
from config import Config

class CurriculumAgent:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL
    
    def generate(self, topic, num_lessons):
        prompt = f"""
        Create a structured curriculum for the topic: "{topic}"
        Generate exactly {num_lessons} lessons.
        
        Each lesson must have:
        1. Title (engaging and descriptive)
        2. Introduction (hook the viewer, 2-3 sentences)
        3. Main Body (core content, 3-4 key points)
        4. Summary/CTA (recap and call-to-action)
        
        Format as JSON with this structure:
        {{
            "topic": "{topic}",
            "lessons": [
                {{
                    "title": "...",
                    "introduction": "...",
                    "main_body": "...",
                    "summary": "..."
                }}
            ]
        }}
        """
        
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert educational content creator."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)