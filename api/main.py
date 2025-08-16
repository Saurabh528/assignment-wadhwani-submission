"""
FastAPI Backend for AI Content Factory
Provides REST APIs for curriculum generation, character management, and video generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from datetime import datetime

# Import our core modules
from agents.curriculum_agent import CurriculumAgent
from core.character_manager import CharacterManager

app = FastAPI(
    title="AI Content Factory API",
    description="AI-driven video generation pipeline",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TopicRequest(BaseModel):
    topic: str
    num_lessons: int = 3
    language: str = "English"

class CurriculumResponse(BaseModel):
    topic: str
    lessons: List[Dict]
    created_at: str

class CharacterRequest(BaseModel):
    name: str
    description: str
    voice_style: str
    gender: str
    generate_avatar: bool = False

class CharacterResponse(BaseModel):
    id: int
    name: str
    description: str
    voice_style: str
    gender: str
    avatar_path: Optional[str]
    created_at: str
    usage_count: int

class VideoGenerationRequest(BaseModel):
    curriculum_id: str
    character_names: Optional[List[str]] = []
    use_avatar_videos: bool = False
    use_lip_sync: bool = False
    video_length: int = 90

class VideoGenerationResponse(BaseModel):
    job_id: str
    status: str
    videos: List[str]
    qa_results: Optional[Dict]

# Global instances
curriculum_agent = CurriculumAgent()
character_manager = CharacterManager()

# In-memory storage for demo (use Redis/database in production)
jobs = {}
curricula = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Content Factory API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/curriculum/generate", response_model=CurriculumResponse)
async def generate_curriculum(request: TopicRequest):
    """Generate structured curriculum from topic"""
    try:
        curriculum = await curriculum_agent.generate(request.topic, request.num_lessons)
        
        # Store curriculum with unique ID
        curriculum_id = f"cur_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        curricula[curriculum_id] = {
            **curriculum,
            "id": curriculum_id,
            "language": request.language,
            "created_at": datetime.now().isoformat()
        }
        
        return CurriculumResponse(
            topic=curriculum["topic"],
            lessons=curriculum["lessons"],
            created_at=curricula[curriculum_id]["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/curriculum/{curriculum_id}")
async def get_curriculum(curriculum_id: str):
    """Get curriculum by ID"""
    if curriculum_id not in curricula:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    return curricula[curriculum_id]

@app.get("/api/curriculum")
async def list_curricula():
    """List all generated curricula"""
    return list(curricula.values())

@app.post("/api/characters", response_model=CharacterResponse)
async def create_character(request: CharacterRequest):
    """Create new character"""
    try:
        character_dict = {
            "name": request.name,
            "description": request.description,
            "voice_style": request.voice_style,
            "gender": request.gender
        }
        
        character_id = character_manager.add_character(
            character_dict, 
            generate_avatar=request.generate_avatar
        )
        
        if character_id == -1:
            raise HTTPException(status_code=400, detail="Character with this name already exists")
        
        # Get the created character
        character = character_manager.get_character(request.name)
        
        return CharacterResponse(
            id=character["id"],
            name=character["name"],
            description=character["description"],
            voice_style=character["voice_style"],
            gender=character["gender"],
            avatar_path=character.get("avatar_path"),
            created_at=character["created_at"],
            usage_count=character["usage_count"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters", response_model=List[CharacterResponse])
async def list_characters():
    """List all characters"""
    try:
        characters = character_manager.get_all_characters()
        return [
            CharacterResponse(
                id=char["id"],
                name=char["name"],
                description=char["description"],
                voice_style=char["voice_style"],
                gender=char["gender"],
                avatar_path=char.get("avatar_path"),
                created_at=char["created_at"],
                usage_count=char["usage_count"]
            )
            for char in characters
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/characters/{character_name}")
async def get_character(character_name: str):
    """Get character by name"""
    character = character_manager.get_character(character_name)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return CharacterResponse(
        id=character["id"],
        name=character["name"],
        description=character["description"],
        voice_style=character["voice_style"],
        gender=character["gender"],
        avatar_path=character.get("avatar_path"),
        created_at=character["created_at"],
        usage_count=character["usage_count"]
    )

@app.delete("/api/characters/{character_name}")
async def delete_character(character_name: str):
    """Delete character"""
    success = character_manager.delete_character(character_name)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {"message": f"Character '{character_name}' deleted successfully"}

@app.post("/api/videos/generate")
async def generate_videos(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate videos from curriculum (background task)"""
    # Check if curriculum exists
    if request.curriculum_id not in curricula:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Generate job ID
    job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize job status
    jobs[job_id] = {
        "id": job_id,
        "status": "started",
        "progress": 0,
        "videos": [],
        "error": None,
        "created_at": datetime.now().isoformat()
    }
    
    # Start background task
    background_tasks.add_task(
        generate_videos_task,
        job_id,
        request.curriculum_id,
        request.character_names,
        request.use_avatar_videos,
        request.use_lip_sync,
        request.video_length
    )
    
    return {"job_id": job_id, "status": "started"}

async def generate_videos_task(
    job_id: str,
    curriculum_id: str,
    character_names: List[str],
    use_avatar_videos: bool,
    use_lip_sync: bool,
    video_length: int
):
    """Background task for video generation"""
    try:
        curriculum = curricula[curriculum_id]
        lessons = curriculum["lessons"]
        videos = []
        
        # Update progress
        jobs[job_id]["status"] = "processing"
        
        for i, lesson in enumerate(lessons):
            # Update progress
            jobs[job_id]["progress"] = int((i / len(lessons)) * 100)
            
            # Generate script
            script = await script_agent.generate(lesson, character_names)
            
            # Generate video
            if use_avatar_videos:
                generator = AvatarVideoGenerator(use_sadtalker=use_lip_sync)
                character_name = character_names[0] if character_names else None
                video_path = await generator.create_avatar_video(
                    script, video_length, character_name, not use_lip_sync
                )
            else:
                generator = VideoGenerator()
                video_path = await generator.create_video(script, video_length)
            
            if video_path:
                videos.append(video_path)
        
        # Run QA checks
        qa_results = await qa_agent.run_checks(videos)
        
        # Update job status
        jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "videos": videos,
            "qa_results": qa_results
        })
        
    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.get("/api/videos/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get video generation job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/api/videos/jobs")
async def list_jobs():
    """List all video generation jobs"""
    return list(jobs.values())

@app.post("/api/qa/check")
async def run_qa_checks(video_paths: List[str]):
    """Run quality assurance checks on videos"""
    try:
        qa_results = await qa_agent.run_checks(video_paths)
        return qa_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/health")
async def system_health():
    """System health check"""
    try:
        # Check core components
        health_status = {
            "api": "healthy",
            "database": "healthy" if os.path.exists("characters.db") else "error",
            "curriculum_agent": "healthy",
            "character_manager": "healthy",
            "total_characters": len(character_manager.get_all_characters()),
            "total_curricula": len(curricula),
            "total_jobs": len(jobs),
            "timestamp": datetime.now().isoformat()
        }
        
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)