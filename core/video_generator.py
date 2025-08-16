import os
import tempfile
import subprocess
from typing import Dict, List, Optional
from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from openai import OpenAI
from core.tts_manager import TTSManager
from config import Config
import requests
import io

class VideoGenerator:
    def __init__(self):
        self.resolution = (1920, 1080)
        self.fps = 30
        self.tts_manager = TTSManager()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        # Ensure dummy directories exist
        os.makedirs(Config.DUMMY_IMAGE_DIR, exist_ok=True)
        os.makedirs(Config.DUMMY_SPEECH_DIR, exist_ok=True)
    
    def generate(self, script: Dict, target_duration: int) -> str:
        scenes = script.get('scenes', [])
        if not scenes:
            return None
        output_path = f"output_video_{os.urandom(4).hex()}.mp4"
        
        # If scenes include pre-saved audio paths, use them; otherwise generate and save to dummy folder
        voiceover_paths: list[str | None] = []
        for i, scene in enumerate(scenes):
            if scene.get('audio_path') and os.path.exists(scene['audio_path']):
                voiceover_paths.append(scene['audio_path'])
            elif scene.get('dialogue'):
                target_audio_path = os.path.join(Config.DUMMY_SPEECH_DIR, f"scene_{i+1}.mp3")
                try:
                    self.tts_manager.generate_voiceover(
                        scene['dialogue'],
                        {
                            'gender': scene.get('character_gender', 'Female'),
                            'voice_style': scene.get('voice_style', 'Professional')
                        },
                        target_audio_path
                    )
                    voiceover_paths.append(target_audio_path)
                except Exception as e:
                    print(f"TTS failed for scene {i+1}: {e}")
                    voiceover_paths.append(None)
            else:
                voiceover_paths.append(None)
        
        # Create video clips for each scene with AI-generated images
        clips = []
        for i, scene in enumerate(scenes):
            try:
                clip = self._create_scene_clip(scene, voiceover_paths[i], scene_index=i)
                if clip is not None:
                    clips.append(clip)
            except Exception as e:
                print(f"Failed to create clip for scene {i+1}: {e}")
        
        if not clips:
            print("No clips produced from scenes. Skipping video write.")
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
            
            final_video = concatenate_videoclips(final_clips, method="compose")
        else:
            final_video = clips[0] if clips else None
        
        # Add overlays and captions synced to audio timing
        final_video = self._add_captions_timed(final_video, scenes, voiceover_paths)
        
        # Write the final video
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec='libx264',
            audio_codec='aac'
        )
        
        return output_path
    
    def _create_scene_clip(self, scene: Dict, audio_path: str = None, scene_index: int | None = None) -> VideoClip:
        # Primary duration should come from audio, fallback to scene duration
        duration = scene.get('duration', 5)
        actual_audio_duration = None
        
        # Get actual audio duration first to ensure scene matches speech length
        if audio_path and os.path.exists(audio_path):
            try:
                temp_audio = AudioFileClip(audio_path)
                actual_audio_duration = temp_audio.duration
                duration = actual_audio_duration  # Use audio duration as primary
                temp_audio.close()
            except Exception as e:
                print(f"Error reading audio duration: {e}")
                pass
        
        # Build/derive visual description from dialogue if missing
        visual_description = scene.get('visual')
        if not visual_description:
            try:
                visual_description = self._derive_visual_from_dialogue(scene.get('dialogue', ''), scene.get('character'))
            except Exception:
                visual_description = scene.get('visual', '') or scene.get('dialogue', '') or 'Educational illustration'
        
        # If a pre-saved image exists for this scene, load it; else generate and save
        pre_image_path = scene.get('image_path')
        if pre_image_path and os.path.exists(pre_image_path):
            img = Image.open(pre_image_path).convert('RGB')
            img = img.resize(self.resolution, Image.LANCZOS)
            img_array = np.array(img)
            try:
                base_clip = ImageClip(img_array).with_duration(duration)
            except AttributeError:
                base_clip = ImageClip(img_array, duration=duration)
        else:
            # For longer scenes, generate a short sequence of images to avoid static/blank gaps
            try:
                if duration >= 4:
                    base_clip = self._generate_visual_sequence(
                        visual_description,
                        duration,
                        save_dir=Config.DUMMY_IMAGE_DIR,
                        scene_index=(scene_index or 0)
                    )
                else:
                    base_clip = self._generate_visual(
                        visual_description,
                        duration,
                        save_path=os.path.join(Config.DUMMY_IMAGE_DIR, f"scene_{(scene_index or 0)+1}.png")
                    )
            except Exception:
                base_clip = self._generate_visual(
                    visual_description,
                    duration,
                    save_path=os.path.join(Config.DUMMY_IMAGE_DIR, f"scene_{(scene_index or 0)+1}.png")
                )
        
        # Ensure visual clip duration matches the determined duration
        try:
            base_clip = base_clip.with_duration(duration)
        except AttributeError:
            base_clip = base_clip.set_duration(duration)
        
        # Add audio if available
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            try:
                final_clip = base_clip.with_audio(audio_clip)
            except AttributeError:
                final_clip = base_clip.set_audio(audio_clip)
            return final_clip
        else:
            # Visual only
            return base_clip
    
    def _derive_visual_from_dialogue(self, dialogue: str, character_name: str | None = None) -> str:
        """
        Use the LLM to convert dialogue into a strong image-generation prompt
        that best depicts what is being said.
        """
        dialogue = (dialogue or '').strip()
        if not dialogue:
            return 'Educational, professional illustration of the lesson topic'
        
        sys = (
            "You are a visual prompt engineer. Convert the spoken dialogue into a highly specific, photorealistic image prompt. "
            "Include setting, subject, key objects, composition, lens and depth of field, lighting (cinematic/soft/natural), mood, color palette, and style. "
            "The image must directly reflect the semantics of the dialogue. Avoid any on-image text or watermarks. One vivid sentence only."
        )
        speaker = f" by {character_name}" if character_name else ""
        user = (
            f"Dialogue{speaker}:\n\n{dialogue}\n\n"
            "Write ONE ultra-photorealistic prompt sentence that best depicts this dialogue."
        )
        resp = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user}
            ],
            model=Config.LLM_MODEL,
            temperature=0.4
        )
        return (resp.choices[0].message.content or '').strip()
    
    def _generate_visual(self, description: str, duration: float, save_path: str | None = None) -> VideoClip:
        try:
            # Generate image using OpenAI DALL·E 3
            response = self.client.images.generate(
                model=Config.IMAGE_MODEL,
                prompt=(
                    "Ultra-photorealistic photograph. "
                    f"{description}. Cinematic lighting, shallow depth of field, realistic textures, high detail skin, no text, no watermark."
                ),
                size=Config.IMAGE_SIZE,
                quality=Config.IMAGE_QUALITY,
                n=1,
            )
            
            # Download the generated image from URL
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            img = Image.open(io.BytesIO(image_response.content)).convert("RGB")
            
            # Resize to video resolution
            img = img.resize(self.resolution, Image.LANCZOS)
            # Persist for reuse in dummy assets
            if save_path:
                try:
                    img.save(save_path, format='PNG')
                except Exception as e:
                    print(f"Failed to save generated image: {e}")
            
        except Exception as e:
            # Fallback to simple text-based visual
            print(f"Image generation failed: {e}. Using fallback.")
            img = self._create_fallback_image(description)
        
        # Convert to numpy array and create video clip
        img_array = np.array(img)
        try:
            # Try newer MoviePy syntax first
            clip = ImageClip(img_array).with_duration(duration)
        except AttributeError:
            # Fallback to older MoviePy syntax
            clip = ImageClip(img_array, duration=duration)
        
        return clip

    def _generate_visual_sequence(
        self,
        description: str,
        total_duration: float,
        save_dir: str | None = None,
        scene_index: int = 0
    ) -> VideoClip:
        """
        Generate multiple images for a single scene and stitch them together to cover the
        full audio duration, reducing chances of visible gaps.
        """
        num_images = max(2, min(4, int(total_duration // 2) or 2))
        sub_duration = total_duration / num_images
        subclips: List[VideoClip] = []

        for k in range(num_images):
            try:
                # Small variation hint to encourage diverse frames
                variant_desc = f"{description}. Variation {k+1}, alternate angle or moment"
                response = self.client.images.generate(
                    model=Config.IMAGE_MODEL,
                    prompt=(
                        "Ultra-photorealistic photograph. "
                        f"{variant_desc}. Cinematic lighting, shallow depth of field, realistic textures, no text, no watermark."
                    ),
                    size=Config.IMAGE_SIZE,
                    quality=Config.IMAGE_QUALITY,
                    n=1,
                )
                image_url = response.data[0].url
                image_response = requests.get(image_url)
                img = Image.open(io.BytesIO(image_response.content)).convert("RGB")
            except Exception:
                # Fallback to base image
                img = self._create_fallback_image(description)

            # Persist for reuse if requested
            if save_dir:
                try:
                    os.makedirs(save_dir, exist_ok=True)
                    img.save(os.path.join(save_dir, f"scene_{scene_index+1}_var{k+1}.png"), format='PNG')
                except Exception:
                    pass

            img = img.resize(self.resolution, Image.LANCZOS)
            clip_array = np.array(img)
            try:
                sub_clip = ImageClip(clip_array).with_duration(sub_duration)
            except AttributeError:
                sub_clip = ImageClip(clip_array, duration=sub_duration)
            subclips.append(sub_clip)

        try:
            return concatenate_videoclips(subclips, method="compose")
        except Exception:
            return concatenate_videoclips(subclips)
    
    def _create_fallback_image(self, description: str) -> Image.Image:
        # Create a simple colored background with text as fallback
        img = Image.new('RGB', self.resolution, color=(64, 64, 128))
        draw = ImageDraw.Draw(img)
        
        # Add scene description as text
        font_size = 40
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        wrapped_text = self._wrap_text(description, 50)
        y_position = self.resolution[1] // 3
        
        for line in wrapped_text.split('\n'):
            text_bbox = draw.textbbox((0, 0), line, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x_position = (self.resolution[0] - text_width) // 2
            draw.text((x_position, y_position), line, fill=(255, 255, 255), font=font)
            y_position += font_size + 10
        
        return img
    
    def _add_captions_timed(self, video: VideoClip, scenes: List[Dict], voiceover_paths: List[Optional[str]]) -> VideoClip:
        """
        Add captions synchronized to the actual audio timing per scene without relying on ImageMagick.
        Captions are perfectly synced with audio duration and scene length.
        """
        caption_overlays: List[VideoClip] = []
        current_time: float = 0.0

        for idx, scene in enumerate(scenes):
            # Captions must match the script dialogue exactly
            text = scene.get('dialogue') or ''
            # ALWAYS prioritize audio duration for perfect sync
            duration = float(scene.get('duration', Config.DEFAULT_SCENE_DURATION))
            audio_path = voiceover_paths[idx] if idx < len(voiceover_paths) else None
            
            # Audio duration takes absolute priority for sync
            if audio_path and os.path.exists(audio_path):
                try:
                    audio_clip = AudioFileClip(audio_path)
                    duration = float(audio_clip.duration)  # This is the authoritative duration
                    try:
                        audio_clip.close()
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error getting audio duration for scene {idx}: {e}")
                    pass

            if text:
                # Build a caption image using PIL
                from PIL import Image, ImageDraw, ImageFont
                width, height = self.resolution
                img = Image.new('RGBA', (width, 140), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
                except Exception:
                    font = ImageFont.load_default()

                max_width = width - 80
                words = text.split()
                lines = []
                current = ''
                for w in words:
                    candidate = (current + ' ' + w).strip()
                    bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=2)
                    if bbox[2] <= max_width:
                        current = candidate
                    else:
                        if current:
                            lines.append(current)
                        current = w
                if current:
                    lines.append(current)

                y = 10
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font, stroke_width=2)
                    tw = bbox[2] - bbox[0]
                    x = (width - tw) // 2
                    draw.text((x, y), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
                    y += (bbox[3] - bbox[1]) + 6

                img_clip = ImageClip(np.array(img)).with_start(current_time).with_duration(duration)
                try:
                    img_clip = img_clip.with_position(('center', height - 160))
                except AttributeError:
                    img_clip = img_clip.set_position(('center', height - 160))
                caption_overlays.append(img_clip)

            current_time += duration

        if not caption_overlays:
            return video

        return CompositeVideoClip([video] + caption_overlays)
    
    def _wrap_text(self, text: str, max_chars: int) -> str:
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