import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Models
    LLM_MODEL = "gpt-4.1-mini"
    IMAGE_MODEL = "dall-e-3"  # Use Dall-E 3 for image generation
    TTS_MODEL = "tts-1"
    
    # Image Generation Settings
    IMAGE_SIZE = "1024x1024"  # Options: "1024x1024", "1792x1024", "1024x1792"
    IMAGE_QUALITY = "standard"  # Options: "standard", "hd" - Use "standard" for testing to reduce costs
    IMAGE_QUALITY_PRODUCTION = "standard"  # Quality to use in production mode
    
    # Video Settings
    VIDEO_RESOLUTION = (1920, 1080)
    VIDEO_FPS = 30
    DEFAULT_SCENE_DURATION = 5
    
    # TTS Settings
    TTS_PROVIDER = "openai"
    DEFAULT_VOICE = "alloy"
    AVAILABLE_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    # Database
    DB_PATH = "content_factory.db"
    
    # Output
    OUTPUT_DIR = "generated_videos"
    TEMP_DIR = "temp"
    # Dummy/Test assets
    DUMMY_DIR = "dummy_assets"
    DUMMY_IMAGE_DIR = "dummy_assets/images"
    DUMMY_SPEECH_DIR = "dummy_assets/speeches"
    DUMMY_LESSONS_JSON = "dummy_assets/lessons.json"
    DUMMY_SCRIPT_PATTERN = "dummy_assets/script_lesson_{index}.json"
    
    # Cost Estimation (per unit) - OpenAI Pricing
    COSTS = {
        "llm_per_1k_input_tokens": 0.05,      # GPT-5 input (estimated)
        "llm_per_1k_output_tokens": 0.15,     # GPT-5 output (estimated)
        "tts_per_1k_characters": 0.015,       # TTS-1
        "image_generation": 0.19,             # GPT-image-1 (high quality 1536x1024)
        "video_rendering_per_minute": 0.05,
        "storage_per_gb": 0.02
    }

    @staticmethod
    def estimate_cost(num_lessons, video_length_seconds):
        # Rough estimates
        llm_tokens = num_lessons * 2000  # ~2k tokens per lesson
        tts_characters = num_lessons * 500  # ~500 chars per lesson
        images = num_lessons * 5  # 5 images per lesson
        video_minutes = (video_length_seconds * num_lessons) / 60
        storage_gb = (video_minutes * 0.1)  # ~100MB per minute
        
        cost = {
            "llm_input": (llm_tokens / 1000) * Config.COSTS["llm_per_1k_input_tokens"],
            "llm_output": (llm_tokens / 1000) * Config.COSTS["llm_per_1k_output_tokens"],
            "tts": (tts_characters / 1000) * Config.COSTS["tts_per_1k_characters"],
            "images": images * Config.COSTS["image_generation"],
            "rendering": video_minutes * Config.COSTS["video_rendering_per_minute"],
            "storage": storage_gb * Config.COSTS["storage_per_gb"]
        }
        
        cost["total"] = sum(cost.values())
        
        return cost