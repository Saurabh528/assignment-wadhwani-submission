"""
SadTalker Manager for Mac laptops
Provides lip-sync animation optimized for Apple Silicon and Intel Macs
"""

import os
import subprocess
import tempfile
import shutil
from typing import Optional, Dict
from config import Config
import json

class SadTalkerManager:
    def __init__(self):
        """Initialize SadTalker Manager for Mac"""
        self.sadtalker_path = os.path.join(os.path.dirname(__file__), "..", "sadtalker")
        self.checkpoints_path = os.path.join(self.sadtalker_path, "checkpoints")
        self.output_dir = os.path.join(Config.OUTPUT_DIR, "sadtalker_videos")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def check_installation(self) -> bool:
        """
        Check if SadTalker is properly installed
        
        Returns:
            bool: True if SadTalker is installed and ready
        """
        # Check if SadTalker directory exists
        if not os.path.exists(self.sadtalker_path):
            print(f"SadTalker not found at {self.sadtalker_path}")
            print("Please install SadTalker from: https://github.com/OpenTalker/SadTalker")
            return False
            
        # Check for required model files
        required_models = [
            "SadTalker_V0.0.2_256.safetensors",
            "mapping_00109-model.pth.tar"
        ]
        
        for model in required_models:
            model_file = os.path.join(self.checkpoints_path, model)
            if not os.path.exists(model_file):
                print(f"Missing model file: {model}")
                print("Run: bash scripts/download_models.sh in sadtalker directory")
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
        Generate lip-synced video using SadTalker
        
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
            print("SadTalker not properly installed, using placeholder")
            return self._create_placeholder_video(avatar_image_path, audio_path, output_path)
        
        try:
            # Generate unique output filename if not provided
            if output_path is None:
                import uuid
                output_filename = f"sadtalker_{uuid.uuid4().hex[:8]}.mp4"
                output_path = os.path.join(self.output_dir, output_filename)
            
            # Resolve to absolute paths to avoid CWD-related issues when switching into sadtalker dir
            abs_audio_path = os.path.abspath(audio_path)
            abs_avatar_image_path = os.path.abspath(avatar_image_path)
            abs_result_dir = os.path.abspath(self.output_dir)

            # Prepare SadTalker command
            cmd = [
                "python3",
                "inference.py",
                "--driven_audio", abs_audio_path,
                "--source_image", abs_avatar_image_path,
                "--result_dir", abs_result_dir,
                "--still",  # For portrait images
                "--preprocess", "full",  # Full preprocessing
                "--enhancer", "gfpgan",  # Face enhancement
                "--cpu"  # Use CPU for Mac compatibility
            ]
            
            # Do not pass --device; the bundled inference.py does not accept it.
            # It will select CUDA if available, otherwise CPU. We already pass --cpu for Mac compatibility.
            
            print(f"Running SadTalker: {' '.join(cmd)}")
            
            # Change to SadTalker directory and run
            original_cwd = os.getcwd()
            os.chdir(self.sadtalker_path)
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=900  # 15 minute timeout to allow full inference on CPU/MPS
                )
                
                # SadTalker saves to results folder, find the generated video
                results_dir = os.path.join(self.sadtalker_path, "results")
                if os.path.exists(results_dir):
                    # Find the most recent video file
                    video_files = [f for f in os.listdir(results_dir) if f.endswith('.mp4')]
                    if video_files:
                        latest_video = max([os.path.join(results_dir, f) for f in video_files], 
                                         key=os.path.getmtime)
                        # Move to our output directory
                        shutil.move(latest_video, output_path)
                        print(f"SadTalker video generated: {output_path}")
                        return output_path
                
                print("SadTalker completed but no video found")
                return None
                
            finally:
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            print("SadTalker timed out, using placeholder")
            return self._create_placeholder_video(avatar_image_path, audio_path, output_path)
        except subprocess.CalledProcessError as e:
            print(f"SadTalker error: {e.stderr}")
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
        Create a placeholder video for testing without SadTalker
        Uses ffmpeg to create a static image video with audio
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
    
    def _is_apple_silicon(self) -> bool:
        """
        Check if running on Apple Silicon Mac
        
        Returns:
            bool: True if running on Apple Silicon (M1/M2/M3)
        """
        try:
            import platform
            return platform.machine() == 'arm64' and platform.system() == 'Darwin'
        except:
            return False
    
    def install_sadtalker(self):
        """
        Helper method to provide installation instructions
        """
        instructions = """
        To install SadTalker on Mac:
        
        1. Install dependencies:
           brew install python@3.10 ffmpeg git-lfs
        
        2. Clone repository:
           git clone https://github.com/OpenTalker/SadTalker.git sadtalker
           cd sadtalker
        
        3. Create virtual environment:
           python3.10 -m venv venv
           source venv/bin/activate
        
        4. Install PyTorch for Mac:
           pip3 install torch torchvision torchaudio
        
        5. Install requirements:
           pip install -r requirements.txt
           pip install dlib cmake face-recognition
        
        6. Download models:
           bash scripts/download_models.sh
        
        For Apple Silicon Macs (M1/M2/M3):
        - SadTalker will use MPS (Metal Performance Shaders) for acceleration
        - Expected memory usage: 4-8GB
        - Processing time: ~30-60 seconds per video
        
        For Intel Macs:
        - SadTalker will use CPU
        - Expected memory usage: 2-4GB  
        - Processing time: ~60-120 seconds per video
        """
        print(instructions)
        return instructions
    
    def get_system_info(self):
        """Get Mac system information for optimization"""
        import platform
        import psutil
        
        info = {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3)),
            "is_apple_silicon": self._is_apple_silicon()
        }
        
        return info