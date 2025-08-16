from openai import AsyncOpenAI
import json
from typing import List, Dict
import os
from moviepy import VideoFileClip
import subprocess
from config import Config
import cv2
import numpy as np
from datetime import datetime

class QAAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL
    
    async def run_checks(self, video_paths: List[str]) -> Dict:
        results = {
            'audio_sync': 0,
            'character_consistency': 0,
            'caption_alignment': 0,
            'details': []
        }
        
        for video_path in video_paths:
            if os.path.exists(video_path):
                video_results = self._analyze_video(video_path)
                results['details'].append(video_results)
                
                # Aggregate scores
                results['audio_sync'] += video_results['audio_sync']
                results['character_consistency'] += video_results['character_consistency']
                results['caption_alignment'] += video_results['caption_alignment']
        
        # Calculate averages
        num_videos = len(video_paths)
        if num_videos > 0:
            results['audio_sync'] = results['audio_sync'] / num_videos
            results['character_consistency'] = results['character_consistency'] / num_videos
            results['caption_alignment'] = results['caption_alignment'] / num_videos
        
        # Flag issues
        results['issues'] = self._identify_issues(results)
        
        return results
    
    def _analyze_video(self, video_path: str) -> Dict:
        results = {
            'video_path': video_path,
            'audio_sync': 95,  # Placeholder - would use actual audio analysis
            'character_consistency': 92,  # Placeholder - would use face/voice recognition
            'caption_alignment': 98  # Placeholder - would use OCR and timing analysis
        }
        
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Check basic properties
            results['duration'] = video.duration
            results['fps'] = video.fps
            results['resolution'] = video.size
            
            # Check audio presence
            results['has_audio'] = video.audio is not None
            
            # Simulate quality checks (in production, these would be real implementations)
            if results['has_audio']:
                results['audio_sync'] = self.check_audio_sync(video)
            
            results['character_consistency'] = self.check_character_consistency(video)
            results['caption_alignment'] = self.check_caption_alignment(video)
            
            video.close()
            
        except Exception as e:
            results['error'] = str(e)
            results['audio_sync'] = 0
            results['character_consistency'] = 0
            results['caption_alignment'] = 0
        
        return results
    
    def check_audio_sync(self, video: VideoFileClip) -> float:
        if video.audio is None:
            return 0.0
        
        # Check if audio duration matches video duration
        video_duration = video.duration
        audio_duration = video.audio.duration
        
        if abs(video_duration - audio_duration) < 0.1:
            return 100.0
        else:
            # Calculate sync score based on difference
            diff_percentage = abs(video_duration - audio_duration) / video_duration * 100
            return max(0, 100 - diff_percentage)
    
    def check_character_consistency(self, video: VideoFileClip) -> float:
        return 92.0  # Placeholder score
    
    def check_caption_alignment(self, video: VideoFileClip) -> float:
        return 95.0  # Placeholder score
    
    def _identify_issues(self, results: Dict) -> List[str]:
        issues = []
        
        if results['audio_sync'] < 90:
            issues.append("Audio synchronization needs improvement")
        
        if results['character_consistency'] < 90:
            issues.append("Character consistency issues detected")
        
        if results['caption_alignment'] < 90:
            issues.append("Caption alignment needs adjustment")
        
        return issues
    
    def auto_correct(self, video_path: str, issues: List[str]) -> str:
        corrected_path = video_path.replace('.mp4', '_corrected.mp4')
        
        # Placeholder for auto-correction logic
        # In production, would implement:
        # 1. Audio re-synchronization
        # 2. Caption re-timing
        # 3. Scene re-rendering for consistency issues
        
        # For now, just copy the original
        subprocess.run(['cp', video_path, corrected_path])
        
        return corrected_path