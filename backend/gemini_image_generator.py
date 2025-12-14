import os
import sys
import uuid
from pathlib import Path
from io import BytesIO
import base64
from typing import Optional, Dict, Any, List
import requests
from PIL import Image
import numpy as np
import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.client import configure
from config import GEMINI_API_KEY, GEMINI_API_KEY_BACKUP, GEMINI_IMAGE_GENERATION_MODEL_NAME, GEMINI_IMAGE_EDITING_MODEL_NAME

# Add the parent directory to sys.path to make imports work
# This is needed because this file might be imported from different contexts
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Configuration - Define defaults first using lowercase to avoid constant redefinition errors
base_dir = Path(__file__).parent.parent
static_dir = base_dir / "static"
generated_images_dir = static_dir / "generated_images"
thumbnail_size = (400, 400)
max_image_size = (1024, 1024)

# Try to import config with full module path to satisfy linter
try:
    from backend.config import GENERATED_IMAGES_DIR as config_generated_images_dir, THUMBNAIL_SIZE as config_thumbnail_size, MAX_IMAGE_SIZE as config_max_image_size
    generated_images_dir = config_generated_images_dir
    thumbnail_size = config_thumbnail_size
    max_image_size = config_max_image_size
except ImportError:
    # Fallback for when running directly from backend directory
    try:
        from config import GENERATED_IMAGES_DIR as config_generated_images_dir, THUMBNAIL_SIZE as config_thumbnail_size, MAX_IMAGE_SIZE as config_max_image_size
        generated_images_dir = config_generated_images_dir
        thumbnail_size = config_thumbnail_size
        max_image_size = config_max_image_size
    except ImportError:
        # Keep defaults already defined above
        pass

# Now assign to the global constants (uppercase) - this should only happen once
GENERATED_IMAGES_DIR = generated_images_dir
THUMBNAIL_SIZE = thumbnail_size
MAX_IMAGE_SIZE = max_image_size

# Ensure the generated images directory exists
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

class GeminiImageGenerator:
    def __init__(self):
        self.generated_images_dir = GENERATED_IMAGES_DIR
        self.generation_model_name = GEMINI_IMAGE_GENERATION_MODEL_NAME
        self.editing_model_name = GEMINI_IMAGE_EDITING_MODEL_NAME
        self.generation_model = None
        self.editing_model = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize the Gemini image models with fallback to backup key"""
        try:
            # Try primary API key first
            configure(api_key=GEMINI_API_KEY)
            
            # Initialize generation model
            self.generation_model = GenerativeModel(self.generation_model_name)
            print(f"Gemini image generation model {self.generation_model_name} initialized successfully with primary key")
            
            # Initialize editing model
            self.editing_model = GenerativeModel(self.editing_model_name)
            print(f"Gemini image editing model {self.editing_model_name} initialized successfully with primary key")
        except Exception as e:
            print(f"Error initializing Gemini image models with primary key: {e}")
            try:
                # Fallback to backup API key
                configure(api_key=GEMINI_API_KEY_BACKUP)
                
                # Initialize generation model
                self.generation_model = GenerativeModel(self.generation_model_name)
                print(f"Gemini image generation model {self.generation_model_name} initialized successfully with backup key")
                
                # Initialize editing model
                self.editing_model = GenerativeModel(self.editing_model_name)
                print(f"Gemini image editing model {self.editing_model_name} initialized successfully with backup key")
            except Exception as e2:
                print(f"Error initializing Gemini image models with backup key: {e2}")
                self.generation_model = None
                self.editing_model = None
    
    def generate_image(self, prompt: str, style: str, room_type: str, user_id: Optional[str] = None, image_file: Optional[bytes] = None, features: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an interior design image based on the prompt using Google Gemini.
        """
        try:
            # Generate 4 diverse images with different variations
            image_urls = []
            image_paths = []
            image_ids = []
            
            # Determine which model to use based on whether we have an input image
            if image_file:
                # Use editing model for image-to-image tasks with variations
                for i in range(4):
                    try:
                        # Create varied prompts for more diverse outputs
                        variation_prompts = [
                            f"As a civil engineer, architect, and interior designer, edit this image with significant changes. Key design elements: {prompt}. Additional features: {features if features else 'modern aesthetics'}. Focus on structural elements and ergonomic design.",
                            f"As a professional designer, completely transform this space. Key design elements: {prompt}. Additional features: {features if features else 'contemporary style'}. Emphasize sustainable materials and lighting.",
                            f"As an architectural visualization expert, reimagine this design entirely. Key design elements: {prompt}. Additional features: {features if features else 'luxury finishes'}. Focus on spatial planning and materials.",
                            f"As an interior design specialist, create a bold reinterpretation. Key design elements: {prompt}. Additional features: {features if features else 'unique aesthetics'}. Consider innovative layouts and textures."
                        ]
                        
                        image_data = self._generate_gemini_image_edit(variation_prompts[i], image_file)
                        # Generate a unique filename
                        image_id = str(uuid.uuid4())
                        filename = f"{image_id}_{style}_{room_type}_{i}.png"
                        
                        # Create user directory if authenticated
                        if user_id:
                            user_dir = self.generated_images_dir / user_id
                            user_dir.mkdir(exist_ok=True)
                            image_path = user_dir / filename
                        else:
                            # Guest images in root directory
                            image_path = self.generated_images_dir / filename
                        
                        # Save the generated image
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                        
                        # Create thumbnail
                        try:
                            with Image.open(BytesIO(image_data)) as img:
                                # Create thumbnail with fixed size for consistency
                                thumbnail = img.copy()
                                thumbnail.thumbnail((400, 300), Image.Resampling.LANCZOS)
                                if user_id:
                                    thumbnail_path = self.generated_images_dir / user_id / f"thumb_{filename}"
                                else:
                                    thumbnail_path = self.generated_images_dir / f"thumb_{filename}"
                                thumbnail.save(thumbnail_path, "PNG")
                        except Exception as thumb_error:
                            print(f"Warning: Failed to create thumbnail for image {i}: {thumb_error}")
                        
                        # Create data URI from the image data
                        image_data_uri = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                        
                        image_urls.append(image_data_uri)
                        image_paths.append(f"/static/generated_images/{user_id + '/' if user_id else ''}{filename}")
                        image_ids.append(image_id)
                    except Exception as e:
                        print(f"Warning: Failed to generate image {i}: {e}")
                        continue
            else:
                # Use generation model for text-to-image tasks with variations
                variation_prompts = [
                    f"As a civil engineer, architect, and interior designer, create a professional interior design render of a {style} {room_type}. Key design elements: {prompt}. Additional features: {features if features else 'modern aesthetics'}. Ensure high quality with realistic lighting and materials.",
                    f"As a professional designer, visualize a unique interpretation of a {style} {room_type}. Key design elements: {prompt}. Additional features: {features if features else 'contemporary style'}. Focus on innovative spatial planning.",
                    f"As an architectural visualization expert, render a detailed {style} {room_type} design. Key design elements: {prompt}. Additional features: {features if features else 'luxury finishes'}. Emphasize structural elements and textures.",
                    f"As an interior design specialist, create an artistic representation of a {style} {room_type}. Key design elements: {prompt}. Additional features: {features if features else 'unique aesthetics'}. Consider creative lighting and materials."
                ]
                
                for i in range(4):
                    try:
                        image_data = self._generate_gemini_image(variation_prompts[i])
                        # Generate a unique filename
                        image_id = str(uuid.uuid4())
                        filename = f"{image_id}_{style}_{room_type}_{i}.png"
                        
                        # Create user directory if authenticated
                        if user_id:
                            user_dir = self.generated_images_dir / user_id
                            user_dir.mkdir(exist_ok=True)
                            image_path = user_dir / filename
                        else:
                            # Guest images in root directory
                            image_path = self.generated_images_dir / filename
                        
                        # Save the generated image
                        with open(image_path, "wb") as f:
                            f.write(image_data)
                        
                        # Create thumbnail
                        try:
                            with Image.open(BytesIO(image_data)) as img:
                                # Create thumbnail with fixed size for consistency
                                thumbnail = img.copy()
                                thumbnail.thumbnail((400, 300), Image.Resampling.LANCZOS)
                                if user_id:
                                    thumbnail_path = self.generated_images_dir / user_id / f"thumb_{filename}"
                                else:
                                    thumbnail_path = self.generated_images_dir / f"thumb_{filename}"
                                thumbnail.save(thumbnail_path, "PNG")
                        except Exception as thumb_error:
                            print(f"Warning: Failed to create thumbnail for image {i}: {thumb_error}")
                        
                        # Create data URI from the image data
                        image_data_uri = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                        
                        image_urls.append(image_data_uri)
                        image_paths.append(f"/static/generated_images/{user_id + '/' if user_id else ''}{filename}")
                        image_ids.append(image_id)
                    except Exception as e:
                        print(f"Warning: Failed to generate image {i}: {e}")
                        continue
            
            # Check if we have valid image data
            if not image_urls:
                raise Exception("No image data returned from Gemini")
            
            return {
                "success": True,
                "image_ids": image_ids,
                "image_urls": image_urls,
                "image_paths": image_paths,
                "prompt": prompt,
                "style": style,
                "room_type": room_type,
                "generation_params": {
                    "model": "google-cloud-imagen-placeholder",
                    "steps": 20,
                    "height": 512,
                    "width": 512
                }
            }
            
        except Exception as e:
            print(f"Image generation error: {e}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Image generation failed: {str(e)}")
    
    def _generate_gemini_image(self, prompt: str) -> bytes:
        """
        Generate a new image from text prompt using Google Gemini.
        Returns the image data as bytes.
        """
        try:
            if self.generation_model:
                print(f"Generating image with prompt: {prompt}")
                # Generate image using Gemini
                response = self.generation_model.generate_content([prompt])
                
                # Debug: Print the response structure
                print(f"Response type: {type(response)}")
                print(f"Response attributes: {dir(response)}")
                
                # Extract image data from response
                for candidate in response.candidates:
                    print(f"Candidate type: {type(candidate)}")
                    print(f"Candidate attributes: {dir(candidate)}")
                    for part in candidate.content.parts:
                        print(f"Part type: {type(part)}")
                        print(f"Part attributes: {dir(part)}")
                        if hasattr(part, 'inline_data'):
                            # Get the image data
                            image_data = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            print(f"Found image data with mime type: {mime_type}")
                            print(f"Image data type: {type(image_data)}")
                            print(f"Image data length: {len(image_data) if image_data else 0}")
                            
                            # Check if we actually have image data
                            if image_data and len(image_data) > 0:
                                # If it's already bytes, return it
                                if isinstance(image_data, bytes):
                                    print("Returning image data as bytes")
                                    return image_data
                                
                                # If it's a string, try to decode it
                                if isinstance(image_data, str):
                                    print("Image data is string, trying to decode")
                                    try:
                                        # Try to decode as base64
                                        decoded_data = base64.b64decode(image_data)
                                        print(f"Successfully decoded base64 data, length: {len(decoded_data)}")
                                        return decoded_data
                                    except Exception as decode_error:
                                        print(f"Failed to decode base64: {decode_error}")
                                        # If that fails, treat it as raw binary string data
                                        encoded_data = image_data.encode('latin1')
                                        print(f"Encoded as latin1, length: {len(encoded_data)}")
                                        return encoded_data
                            else:
                                print("Image data is empty or None")
                
                # If we get here, no valid image data was found
                print("No valid image data returned from Gemini")
                raise Exception("Failed to generate image with Gemini. No valid image data returned.")
            else:
                # Raise exception if model not available
                raise Exception("Image generation model is not available. Please check your API key configuration.")
        except Exception as e:
            print(f"Gemini image generation error in _generate_gemini_image: {e}")
            # Re-raise the exception so it can be handled upstream
            raise Exception(f"Failed to generate image: {str(e)}")
    
    def _generate_gemini_image_edit(self, prompt: str, image_data: bytes) -> bytes:
        """
        Edit an existing image based on a text prompt using Google Gemini.
        Returns the edited image data as bytes.
        """
        try:
            if self.editing_model:
                # Convert bytes to PIL Image
                image = Image.open(BytesIO(image_data))
                
                # Generate edited image using Gemini
                response = self.editing_model.generate_content([prompt, image])
                
                # Debug: Print the response structure
                print(f"Editing response type: {type(response)}")
                print(f"Editing response attributes: {dir(response)}")
                
                # Extract image data from response
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data'):
                                    # Get the image data
                                    edited_image_data = part.inline_data.data
                                    mime_type = part.inline_data.mime_type
                                    print(f"Found edited image data with mime type: {mime_type}")
                                    print(f"Edited image data type: {type(edited_image_data)}")
                                    print(f"Edited image data length: {len(edited_image_data) if edited_image_data else 0}")
                                    
                                    # Check if we actually have image data
                                    if edited_image_data and len(edited_image_data) > 0:
                                        # If it's already bytes, return it
                                        if isinstance(edited_image_data, bytes):
                                            print("Returning edited image data as bytes")
                                            return edited_image_data
                                        
                                        # If it's a string, try to decode it
                                        if isinstance(edited_image_data, str):
                                            print("Edited image data is string, trying to decode")
                                            try:
                                                # Try to decode as base64
                                                return base64.b64decode(edited_image_data)
                                            except Exception:
                                                # If that fails, treat it as raw binary string data
                                                return edited_image_data.encode('latin1')
                                else:
                                    print("Edited image data is empty or None")
            
                # If we get here, no valid image data was found
                print("No valid edited image data returned from Gemini")
                raise Exception("Failed to edit image with Gemini. No valid image data returned.")
            else:
                # Raise exception if model not available
                raise Exception("Image editing model is not available. Please check your API key configuration.")
        except Exception as e:
            print(f"Gemini image editing error in _generate_gemini_image_edit: {e}")
            import traceback
            traceback.print_exc()
            # Raise exception if editing fails
            raise Exception(f"Failed to edit image: {str(e)}")
    
    def _download_and_save_image(self, url: str, image_path: Path, thumbnail_path: Path):
        """Download image from URL and create thumbnail"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Save original image
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            # Create thumbnail
            with Image.open(image_path) as img:
                img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, "JPEG", quality=85)
                
        except Exception as e:
            print(f"Error downloading/saving image: {e}")
    
    def generate_from_floor_plan(self, floor_plan_path: str, style: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate interior design from uploaded floor plan.
        This would use ControlNet or similar for layout-aware generation.
        """
        try:
            # For now, we'll generate a placeholder image
            return self._generate_mock_image(f"Interior design based on uploaded floor plan in {style} style", style, "floor_plan_based", user_id)
        except Exception as e:
            print(f"Error generating from floor plan: {e}")
            # Fallback to regular generation
            return self._generate_mock_image(f"Interior design in {style} style", style, "floor_plan_based", user_id)
    
    def _generate_mock_image(self, prompt: str, style: str, room_type: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a mock image for testing purposes"""
        # Generate a simple colored image with text
        width, height = 512, 512
        # Create a random color based on style
        colors = {
            "modern": (50, 50, 50),
            "scandinavian": (240, 240, 240),
            "industrial": (100, 100, 100),
            "bohemian": (200, 150, 100),
            "eco-friendly": (150, 200, 150),
        }
        color = colors.get(style.lower(), (100, 100, 200))
        
        image = Image.new('RGB', (width, height), color=color)
        
        # Add text to the image
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = f"{style.title()} {room_type.title()}\nDesign Generated"
        text_position = (50, 200)
        draw.text(text_position, text, fill=(255, 255, 255), font=font)
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Save the generated image
        image_id = str(uuid.uuid4())
        filename = f"{image_id}_{style}_{room_type}.png"
        
        # Create user directory if authenticated
        if user_id:
            user_dir = self.generated_images_dir / user_id
            user_dir.mkdir(exist_ok=True)
            image_path = user_dir / filename
            thumbnail_path = user_dir / f"thumb_{filename}"
        else:
            # Guest images in root directory
            image_path = self.generated_images_dir / filename
            thumbnail_path = self.generated_images_dir / f"thumb_{filename}"
        
        # Save the generated image
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(img_str))
        
        # Create thumbnail
        with Image.open(image_path) as img:
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "PNG")
        
        return {
            "success": True,
            "image_id": image_id,
            "image_url": f"/static/generated_images/{user_id + '/' if user_id else ''}{filename}",
            "image_urls": [f"data:image/png;base64,{img_str}"],
            "image_paths": [f"/static/generated_images/{user_id + '/' if user_id else ''}{filename}"],
            "prompt": prompt,
            "style": style,
            "room_type": room_type,
            "generation_params": {
                "model": "mock_generator",
                "steps": 10,
                "height": 512,
                "width": 512
            }
        }
    
    def cleanup_guest_images(self, days_old: int = 30):
        """Clean up old guest images"""
        import time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        
        for image_file in self.generated_images_dir.glob("*.png"):
            if image_file.stat().st_mtime < cutoff_time:
                try:
                    image_file.unlink()
                    # Also remove thumbnail
                    thumb_file = self.generated_images_dir / f"thumb_{image_file.name}"
                    if thumb_file.exists():
                        thumb_file.unlink()
                except Exception as e:
                    print(f"Error cleaning up {image_file}: {e}")

# Global image generator instance
gemini_image_generator = GeminiImageGenerator()