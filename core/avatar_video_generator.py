"""
Avatar Video Generator for creating split-screen educational videos
with lip-synced avatars and educational content
"""

import os
import tempfile
import subprocess
from typing import Dict, List, Optional
# Import moviepy classes as needed to avoid import issues
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.video.VideoClip import VideoClip, ImageClip
except ImportError:
    # Fallback imports for different moviepy versions
    try:
        from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
        from moviepy.video.VideoClip import VideoClip, ImageClip
    except ImportError:
        # Minimal imports - we'll import as needed
        pass
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from openai import OpenAI
from core.tts_manager import TTSManager
from core.sadtalker_manager import SadTalkerManager
from core.character_manager import CharacterManager
from config import Config
import requests
import io

class AvatarVideoGenerator:
    def __init__(self, use_sadtalker: bool = False):
        """
        Initialize Avatar Video Generator
        
        Args:
            use_sadtalker: If True, uses SadTalker for lip-sync animation
        """
        self.resolution = Config.VIDEO_RESOLUTION
        self.fps = Config.VIDEO_FPS
        self.tts_manager = TTSManager()
        self.sadtalker_manager = SadTalkerManager() if use_sadtalker else None
        self.character_manager = CharacterManager()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Layout configuration
        self.avatar_width = self.resolution[0] // 4  # 1/4 of screen width
        self.content_width = self.resolution[0] - self.avatar_width  # 3/4 of screen width
        
        # Ensure output directories exist
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.join(Config.OUTPUT_DIR, "avatar_videos"), exist_ok=True)
    
    def create_avatar_video(
        self,
        script: Dict,
        target_duration: int,
        character_name: Optional[str] = None,
        use_placeholder: bool = True
    ) -> str:
        """
        Create a video with avatar on the left and educational content on the right
        
        Args:
            script: Video script with scenes
            target_duration: Target video duration
            character_name: Name of the character to use as avatar
            use_placeholder: If True, uses placeholder for lip-sync (for testing)
            
        Returns:
            Path to the generated video
        """
        scenes = script.get('scenes', [])
        if not scenes:
            return None
        
        output_path = os.path.join(Config.OUTPUT_DIR, "avatar_videos", f"avatar_video_{os.urandom(4).hex()}.mp4")
        
        # Get character and avatar
        character = None
        avatar_path = None
        if character_name:
            character = self.character_manager.get_character(character_name)
            if character:
                avatar_path = character.get('avatar_path')
                # Validate avatar_path is actually a file path
                if avatar_path and not os.path.exists(avatar_path):
                    print(f"Invalid avatar path for {character_name}: {avatar_path}")
                    avatar_path = None
        
        # If no avatar, use first available character with avatar
        if not avatar_path:
            all_characters = self.character_manager.get_all_characters()
            for char in all_characters:
                if char.get('avatar_path') and os.path.exists(char['avatar_path']):
                    character = char
                    avatar_path = char['avatar_path']
                    break
        
        # If still no valid avatar, generate a placeholder
        if not avatar_path and character:
            from core.avatar_manager import AvatarManager
            avatar_manager = AvatarManager(test_mode=True)
            avatar_path = avatar_manager.create_placeholder_avatar(character.get('name', 'default'))
        
        # Generate audio for all scenes
        audio_paths = self._generate_all_audio(scenes, character)
        
        # Create video clips for each scene
        clips = []
        for i, scene in enumerate(scenes):
            try:
                if avatar_path and audio_paths[i]:
                    # Create split-screen clip with avatar
                    clip = self._create_avatar_scene_clip(
                        scene,
                        avatar_path,
                        audio_paths[i],
                        scene_index=i,
                        use_placeholder=use_placeholder
                    )
                else:
                    # Fallback to regular scene clip
                    clip = self._create_regular_scene_clip(
                        scene,
                        audio_paths[i],
                        scene_index=i
                    )
                
                if clip is not None:
                    clips.append(clip)
            except Exception as e:
                print(f"Failed to create clip for scene {i+1}: {e}")
        
        if not clips:
            print("No clips produced from scenes.")
            return None
        
        # Create smooth transitions between scenes to eliminate blackouts
        if len(clips) > 1:
            # Add crossfade transitions between scenes
            transition_duration = 0.5  # 0.5 second crossfade
            final_clips = [clips[0]]  # Start with first clip
            
            for i in range(1, len(clips)):
                # Apply crossfade transition
                try:
                    # Crossfade the end of previous clip with start of current clip
                    prev_clip = final_clips[-1]
                    curr_clip = clips[i]
                    
                    # Ensure clips have minimum duration for crossfade
                    if prev_clip.duration > transition_duration and curr_clip.duration > transition_duration:
                        try:
                            # Apply crossfade using newer MoviePy syntax
                            curr_clip = curr_clip.with_crossfadein(transition_duration)
                        except AttributeError:
                            # Fallback for older MoviePy versions
                            from moviepy.video.fx import crossfadein
                            curr_clip = crossfadein(curr_clip, transition_duration)
                except Exception as e:
                    print(f"Crossfade failed for clip {i}: {e}, using direct concatenation")
                    pass
                
                final_clips.append(curr_clip)
            
            final_video = concatenate_videoclips(final_clips)
        else:
            final_video = clips[0] if clips else None
        
        # Add captions synchronized with audio durations
        final_video = self._add_captions_timed(final_video, scenes, audio_paths)
        
        # Write the final video
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            threads=4
        )
        
        print(f"Avatar video created: {output_path}")
        return output_path
    
    def _generate_all_audio(
        self,
        scenes: List[Dict],
        character: Optional[Dict] = None
    ) -> List[Optional[str]]:
        """
        Generate audio files for all scenes
        
        Args:
            scenes: List of scene dictionaries
            character: Character information for voice selection
            
        Returns:
            List of audio file paths
        """
        audio_paths = []
        
        for i, scene in enumerate(scenes):
            if scene.get('audio_path') and os.path.exists(scene['audio_path']):
                audio_paths.append(scene['audio_path'])
            elif scene.get('dialogue'):
                audio_dir = os.path.join(Config.OUTPUT_DIR, "audio")
                os.makedirs(audio_dir, exist_ok=True)
                audio_path = os.path.join(audio_dir, f"scene_{i+1}_{os.urandom(4).hex()}.mp3")
                
                try:
                    # Use character voice settings if available
                    voice_settings = {
                        'gender': character.get('gender', 'Female') if character else 'Female',
                        'voice_style': character.get('voice_style', 'Professional') if character else 'Professional'
                    }
                    
                    self.tts_manager.generate_voiceover(
                        scene['dialogue'],
                        voice_settings,
                        audio_path
                    )
                    audio_paths.append(audio_path)
                except Exception as e:
                    print(f"TTS failed for scene {i+1}: {e}")
                    audio_paths.append(None)
            else:
                audio_paths.append(None)
        
        return audio_paths
    
    def _create_avatar_scene_clip(
        self,
        scene: Dict,
        avatar_path: str,
        audio_path: str,
        scene_index: int,
        use_placeholder: bool = True
    ):
        """
        Create a split-screen clip with avatar on left and content on right
        
        Args:
            scene: Scene dictionary
            avatar_path: Path to avatar image
            audio_path: Path to audio file
            scene_index: Index of the scene
            use_placeholder: If True, uses static avatar instead of lip-sync
            
        Returns:
            Video clip with split-screen layout
        """
        # Primary duration should come from audio, fallback to scene duration
        duration = scene.get('duration', 5)
        
        # Get actual audio duration first to ensure scene matches speech length
        if audio_path and os.path.exists(audio_path):
            try:
                temp_audio = AudioFileClip(audio_path)
                duration = temp_audio.duration  # Use audio duration as primary
                temp_audio.close()
            except Exception as e:
                print(f"Error reading audio duration: {e}")
                pass
        
        # Generate lip-synced avatar video
        if self.sadtalker_manager and not use_placeholder:
            avatar_video_path = self.sadtalker_manager.generate_lip_sync_video(
                avatar_path,
                audio_path,
                use_placeholder=use_placeholder
            )
        else:
            # Create placeholder avatar video (static image with audio)
            avatar_video_path = self._create_static_avatar_video(
                avatar_path,
                audio_path,
                duration
            )
        
        # Generate educational content for the right side
        content_clip = self._generate_content_visual(
            scene,
            duration,
            scene_index
        )
        
        # Load avatar video
        if avatar_video_path and os.path.exists(avatar_video_path):
            avatar_clip = VideoFileClip(avatar_video_path)
            # Resize to 1/4 width - using resize method with new width
            try:
                avatar_clip = avatar_clip.resized(width=self.avatar_width)
            except AttributeError:
                # Fallback for older MoviePy versions
                from moviepy.video.fx import resize
                avatar_clip = resize(avatar_clip, width=self.avatar_width)
            # Position on the left
            try:
                avatar_clip = avatar_clip.with_position(("left", "center"))
            except AttributeError:
                avatar_clip = avatar_clip.set_position(("left", "center"))
        else:
            # Create placeholder avatar clip
            avatar_clip = self._create_placeholder_avatar_clip(duration)
        
        # Resize content to 3/4 width and position on the right
        try:
            content_clip = content_clip.resized(width=self.content_width)
        except AttributeError:
            # Fallback for older MoviePy versions
            from moviepy.video.fx import resize
            content_clip = resize(content_clip, width=self.content_width)
        try:
            content_clip = content_clip.with_position((self.avatar_width, "center"))
        except AttributeError:
            content_clip = content_clip.set_position((self.avatar_width, "center"))
        
        # Composite the clips
        composite_clip = CompositeVideoClip(
            [avatar_clip, content_clip],
            size=self.resolution
        )
        
        # Add audio if available
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            try:
                composite_clip = composite_clip.with_audio(audio_clip)
            except AttributeError:
                composite_clip = composite_clip.set_audio(audio_clip)
        
        return composite_clip
    
    def _create_regular_scene_clip(
        self,
        scene: Dict,
        audio_path: Optional[str],
        scene_index: int
    ):
        """
        Create a regular full-screen scene clip (fallback when no avatar)
        
        Args:
            scene: Scene dictionary
            audio_path: Path to audio file
            scene_index: Index of the scene
            
        Returns:
            Video clip
        """
        # Primary duration should come from audio, fallback to scene duration
        duration = scene.get('duration', 5)
        
        # Get actual audio duration first to ensure scene matches speech length
        if audio_path and os.path.exists(audio_path):
            try:
                temp_audio = AudioFileClip(audio_path)
                duration = temp_audio.duration  # Use audio duration as primary
                temp_audio.close()
            except Exception as e:
                print(f"Error reading audio duration for regular scene: {e}")
                pass
        
        # Generate visual content
        visual_clip = self._generate_content_visual(scene, duration, scene_index)
        
        # Ensure visual duration matches determined duration first
        try:
            visual_clip = visual_clip.with_duration(duration)
        except AttributeError:
            visual_clip = visual_clip.set_duration(duration)
            
        # Add audio if available
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            try:
                visual_clip = visual_clip.with_audio(audio_clip)
            except AttributeError:
                visual_clip = visual_clip.set_audio(audio_clip)
        
        return visual_clip
    
    def _generate_content_visual(
        self,
        scene: Dict,
        duration: float,
        scene_index: int
    ):
        """
        Generate educational content visual for the scene
        
        Args:
            scene: Scene dictionary
            duration: Duration of the clip
            scene_index: Index of the scene
            
        Returns:
            Video clip with educational content
        """
        visual_description = scene.get('visual', '')
        if not visual_description and scene.get('dialogue'):
            # Derive visual from dialogue
            visual_description = self._derive_visual_from_dialogue(
                scene['dialogue'],
                scene.get('character')
            )
        
        # Check for pre-saved image
        if scene.get('image_path') and os.path.exists(scene['image_path']):
            img = Image.open(scene['image_path']).convert('RGB')
        else:
            # Generate new image
            img = self._generate_image(visual_description, scene_index)
        
        # Convert to video clip
        img_array = np.array(img)
        try:
            clip = ImageClip(img_array).with_duration(duration)
        except AttributeError:
            clip = ImageClip(img_array, duration=duration)
        
        return clip
    
    def _generate_image(self, description: str, scene_index: int) -> Image.Image:
        """
        Generate an educational image using DALL-E
        
        Args:
            description: Visual description
            scene_index: Index of the scene
            
        Returns:
            Generated image
        """
        try:
            # Use configured quality setting
            quality = Config.IMAGE_QUALITY if hasattr(Config, 'IMAGE_QUALITY') else 'low'
            size = Config.IMAGE_SIZE if hasattr(Config, 'IMAGE_SIZE') else '1024x1024'
            
            response = self.client.images.generate(
                model=Config.IMAGE_MODEL,
                prompt=f"Educational illustration: {description}. Professional, clean, suitable for learning content.",
                size=size,
                quality=quality,
                n=1
            )
            
            # Download image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            img = Image.open(io.BytesIO(image_response.content)).convert("RGB")
            
            # Save for reuse
            save_dir = os.path.join(Config.OUTPUT_DIR, "generated_images")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"scene_{scene_index+1}_{os.urandom(4).hex()}.png")
            img.save(save_path)
            
            return img
            
        except Exception as e:
            print(f"Image generation failed: {e}. Using fallback.")
            return self._create_fallback_image(description)
    
    def _derive_visual_from_dialogue(self, dialogue: str, character_name: Optional[str] = None) -> str:
        """
        Convert dialogue into a visual description
        
        Args:
            dialogue: The dialogue text
            character_name: Name of the speaking character
            
        Returns:
            Visual description for image generation
        """
        if not dialogue:
            return "Educational professional illustration"
        
        prompt = f"Convert this dialogue into a concise image prompt: {dialogue}"
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=Config.LLM_MODEL,
            temperature=0.4,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    def _create_static_avatar_video(
        self,
        avatar_path: str,
        audio_path: str,
        duration: float
    ) -> str:
        """
        Create a static avatar video (placeholder for lip-sync)
        
        Args:
            avatar_path: Path to avatar image
            audio_path: Path to audio file
            duration: Duration of the video
            
        Returns:
            Path to generated video
        """
        output_dir = os.path.join(Config.OUTPUT_DIR, "temp_avatar_videos")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"static_avatar_{os.urandom(4).hex()}.mp4")
        
        # Validate avatar path
        if not avatar_path or not os.path.exists(avatar_path):
            print(f"Invalid avatar path: {avatar_path}, creating placeholder")
            # Create a placeholder image if avatar doesn't exist
            from core.avatar_manager import AvatarManager
            avatar_manager = AvatarManager(test_mode=True)
            avatar_path = avatar_manager.create_placeholder_avatar("default")
        
        try:
            # Create video from static image with audio using ffmpeg
            cmd = [
                "ffmpeg",
                "-loop", "1",
                "-i", avatar_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "copy",
                "-shortest",
                "-pix_fmt", "yuv420p",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except Exception as e:
            print(f"Error creating static avatar video: {e}")
            return None
    
    def _create_placeholder_avatar_clip(self, duration: float):
        """
        Create a placeholder avatar clip when no avatar is available
        
        Args:
            duration: Duration of the clip
            
        Returns:
            Placeholder video clip
        """
        # Create a gray placeholder image
        img = Image.new('RGB', (self.avatar_width, self.resolution[1]), color='gray')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = "Avatar\nPlaceholder"
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((self.avatar_width - text_width) // 2, (self.resolution[1] - text_height) // 2)
        draw.text(position, text, fill='white', font=font)
        
        img_array = np.array(img)
        try:
            clip = ImageClip(img_array).with_duration(duration)
        except AttributeError:
            clip = ImageClip(img_array, duration=duration)
        
        return clip
    
    def _create_fallback_image(self, description: str) -> Image.Image:
        """
        Create a fallback image when generation fails
        
        Args:
            description: Text description
            
        Returns:
            Fallback image
        """
        img = Image.new('RGB', (1024, 1024), color=(64, 64, 128))
        draw = ImageDraw.Draw(img)
        
        # Add text
        wrapped_text = self._wrap_text(description, 40)
        y_position = 400
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        except:
            font = ImageFont.load_default()
        
        for line in wrapped_text.split('\n'):
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x_position = (1024 - text_width) // 2
            draw.text((x_position, y_position), line, fill='white', font=font)
            y_position += 40
        
        return img
    
    def _add_captions_timed(self, video, scenes: List[Dict], audio_paths: List[Optional[str]]):
        """
        Add captions synced to scene audio timings using PIL overlays (no ImageMagick/TextClip).
        """
        overlays: List[VideoClip] = []
        current_time: float = 0.0
        video_width, video_height = self.resolution

        for idx, scene in enumerate(scenes):
            # Captions must match the script dialogue exactly
            text = scene.get('dialogue') or ''
            # ALWAYS prioritize audio duration for perfect sync
            duration = float(scene.get('duration', 5))
            audio_path = audio_paths[idx] if idx < len(audio_paths) else None
            
            # Audio duration takes absolute priority for sync
            if audio_path and os.path.exists(audio_path):
                try:
                    ac = AudioFileClip(audio_path)
                    duration = float(ac.duration)  # This is the authoritative duration
                    try:
                        ac.close()
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error getting audio duration for scene {idx}: {e}")
                    pass

            if text:
                # Render caption image
                from PIL import Image, ImageDraw, ImageFont
                caption_height = 140
                img = Image.new('RGBA', (video_width, caption_height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
                except Exception:
                    font = ImageFont.load_default()

                max_width = video_width - 80
                words = text.split()
                lines: List[str] = []
                current_line = ''
                for w in words:
                    candidate = (current_line + ' ' + w).strip()
                    bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=2)
                    if bbox[2] <= max_width:
                        current_line = candidate
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = w
                if current_line:
                    lines.append(current_line)

                y = 10
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font, stroke_width=2)
                    tw = bbox[2] - bbox[0]
                    x = (video_width - tw) // 2
                    draw.text((x, y), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
                    y += (bbox[3] - bbox[1]) + 6

                cap_clip = ImageClip(np.array(img)).with_start(current_time).with_duration(duration)
                try:
                    cap_clip = cap_clip.with_position(('center', video_height - 160))
                except AttributeError:
                    cap_clip = cap_clip.set_position(('center', video_height - 160))
                overlays.append(cap_clip)

            current_time += duration

        if overlays:
            return CompositeVideoClip([video] + overlays)
        return video
    
    def _wrap_text(self, text: str, max_chars: int) -> str:
        """
        Wrap text to fit within character limit
        
        Args:
            text: Text to wrap
            max_chars: Maximum characters per line
            
        Returns:
            Wrapped text
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)