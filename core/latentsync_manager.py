"""
LatentSync Manager for lip-sync animation
This module handles the integration with LatentSync for creating lip-synced avatar videos
"""

import os
import subprocess
import tempfile
import shutil
from typing import Optional, Dict
from config import Config
import json

class LatentSyncManager:
    def __init__(self):
        """Initialize LatentSync Manager"""
        self.latentsync_path = os.path.join(os.path.dirname(__file__), "..", "latentsync")
        self.model_path = os.path.join(self.latentsync_path, "models")
        self.output_dir = os.path.join(Config.OUTPUT_DIR, "lip_sync_videos")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def check_installation(self) -> bool:
        """
        Check if LatentSync is properly installed
        
        Returns:
            bool: True if LatentSync is installed and ready
        """
        # Check if LatentSync directory exists
        if not os.path.exists(self.latentsync_path):
            print(f"LatentSync not found at {self.latentsync_path}")
            print("Please install LatentSync from: https://github.com/bytedance/LatentSync")
            return False
            
        # Check for required model files
        required_models = ["latentsync_unet.pt", "stable_syncnet.pt"]
        for model in required_models:
            model_file = os.path.join(self.model_path, model)
            if not os.path.exists(model_file):
                print(f"Missing model file: {model}")
                print("Please download models from LatentSync repository")
                return False
                
        return True
    
    def generate_lip_sync_video(
        self,
        avatar_image_path: str,
        audio_path: str,
        output_path: Optional[str] = None,
        use_placeholder: bool = False
    ) -> Optional[str]:
        """
        Generate lip-synced video using LatentSync
        
        Args:
            avatar_image_path: Path to the avatar image
            audio_path: Path to the audio file
            output_path: Optional output path for the video
            use_placeholder: If True, creates a placeholder video for testing
            
        Returns:
            Path to the generated video or None if failed
        """
        if use_placeholder:
            return self._create_placeholder_video(avatar_image_path, audio_path, output_path)
        
        if not self.check_installation():
            print("LatentSync not properly installed, using placeholder")
            return self._create_placeholder_video(avatar_image_path, audio_path, output_path)
        
        try:
            # Generate unique output filename if not provided
            if output_path is None:
                import uuid
                output_filename = f"lip_sync_{uuid.uuid4().hex[:8]}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
            
            # Prepare LatentSync command
            cmd = [
                "python3",
                os.path.join(self.latentsync_path, "inference.py"),
                "--source_image", avatar_image_path,
                "--driven_audio", audio_path,
                "--output", output_path,
                "--model_path", self.model_path,
                "--device", "cuda" if self._check_cuda() else "cpu"
            ]
            
            print(f"Running LatentSync: {' '.join(cmd)}")
            
            # Run LatentSync
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if os.path.exists(output_path):
                print(f"Lip-sync video generated: {output_path}")
                return output_path
            else:
                print("LatentSync failed to generate video")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"LatentSync error: {e.stderr}")
            return self._create_placeholder_video(avatar_image_path, audio_path, output_path)
        except Exception as e:
            print(f"Error generating lip-sync video: {str(e)}")
            return self._create_placeholder_video(avatar_image_path, audio_path, output_path)
    
    def _create_placeholder_video(
        self,
        avatar_image_path: str,
        audio_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Create a placeholder video for testing without LatentSync
        Uses ffmpeg to create a static image video with audio
        
        Args:
            avatar_image_path: Path to the avatar image
            audio_path: Path to the audio file
            output_path: Optional output path for the video
            
        Returns:
            Path to the generated placeholder video
        """
        if output_path is None:
            import uuid
            output_filename = f"placeholder_{uuid.uuid4().hex[:8]}.mp4"
            output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # Get audio duration
            duration_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ]
            
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
            duration = float(duration_result.stdout.strip())
            
            # Create video from static image with audio
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", avatar_image_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                "-shortest",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Placeholder video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error creating placeholder video: {str(e)}")
            return None
    
    def _check_cuda(self) -> bool:
        """
        Check if CUDA is available
        
        Returns:
            bool: True if CUDA is available
        """
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def install_latentsync(self):
        """
        Helper method to install LatentSync
        This provides instructions for manual installation
        """
        instructions = """
        To install LatentSync:
        
        1. Clone the repository:
           git clone https://github.com/bytedance/LatentSync.git latentsync
        
        2. Install dependencies:
           cd latentsync
           pip install -r requirements.txt
        
        3. Download model files:
           - Download latentsync_unet.pt (~5GB)
           - Download stable_syncnet.pt (~1.6GB)
           - Place them in latentsync/models/
        
        4. For GPU support:
           pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        
        Note: LatentSync requires 20-30GB VRAM for optimal performance.
        """
        print(instructions)
        return instructions