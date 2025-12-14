import google.generativeai as genai
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
import os
import json
from typing import Dict, List, Optional, Any
from config import GEMINI_API_KEY, GEMINI_API_KEY_BACKUP, GEMINI_TEXT_MODEL_NAME

class GeminiClient:
    def __init__(self):
        # Configure the API key
        configure(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_TEXT_MODEL_NAME
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the Gemini model with fallback to backup key"""
        try:
            # Try primary API key first
            configure(api_key=GEMINI_API_KEY)
            self.model = GenerativeModel(self.model_name)
            print(f"Gemini model {self.model_name} initialized successfully with primary key")
        except Exception as e:
            print(f"Error initializing Gemini model with primary key: {e}")
            try:
                # Fallback to backup API key
                configure(api_key=GEMINI_API_KEY_BACKUP)
                self.model = GenerativeModel(self.model_name)
                print(f"Gemini model {self.model_name} initialized successfully with backup key")
            except Exception as e2:
                print(f"Error initializing Gemini model with backup key: {e2}")
                self.model = None
    
    def generate_response(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """Generate a response using Gemini"""
        try:
            # Prepare the conversation context
            conversation_history = []
            
            # Add system prompt for interior design context
            system_prompt = """You are an expert interior designer AI assistant. You help users with:
            - Interior design recommendations and style advice
            - Color palette suggestions based on room type and preferences
            - Furniture and decor recommendations
            - Space planning and layout optimization
            - Eco-friendly and sustainable design options
            - Pet-friendly design considerations
            
            Provide helpful, creative, and practical advice. Keep responses conversational and engaging."""
            
            conversation_history.append({"role": "user", "parts": [system_prompt]})
            conversation_history.append({"role": "model", "parts": ["Understood. I'm ready to help with interior design questions."]})
            
            # Add conversation context if provided
            if context:
                for msg in context:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "system":
                        # Convert system messages to user messages for Gemini
                        conversation_history.append({"role": "user", "parts": [content]})
                        conversation_history.append({"role": "model", "parts": ["Understood."]})
                    elif role == "user":
                        conversation_history.append({"role": "user", "parts": [content]})
                    elif role == "assistant":
                        conversation_history.append({"role": "model", "parts": [content]})
            
            # Add current user message
            conversation_history.append({"role": "user", "parts": [prompt]})
            
            # Generate response using the chat context
            if self.model:
                chat = self.model.start_chat(history=conversation_history[:-1])  # Exclude the last message
                response = chat.send_message(conversation_history[-1]["parts"][0])
                return response.text
            else:
                # Raise exception if model is not available
                raise Exception("Text generation model is not available. Please check your API key configuration.")
            
        except Exception as e:
            print(f"Gemini error in generate_response: {e}")
            raise Exception(f"Failed to generate text response: {str(e)}")
    
    def generate_design_suggestions(self, room_type: str, style: str, prompt: str) -> Dict[str, Any]:
        """Generate specific design suggestions for a room"""
        design_prompt = f"""
        Generate interior design suggestions for a {room_type} in {style} style.
        User request: {prompt}
        
        Please provide:
        1. Color palette (3-4 colors with hex codes)
        2. Key furniture pieces (3-5 items)
        3. Lighting recommendations
        4. Material suggestions
        5. Decor elements
        
        Format as JSON with clear categories.
        """
        
        try:
            if self.model:
                response = self.model.generate_content(design_prompt)
                response_text = response.text
                
                # Try to parse as JSON, fallback to structured text
                try:
                    # Clean up the response text to make it valid JSON
                    cleaned_response = response_text.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]  # Remove ```json
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]  # Remove ```
                    
                    return json.loads(cleaned_response)
                except:
                    return {"suggestions": response_text}
            else:
                return self._get_fallback_design_suggestions(room_type, style)
                
        except Exception as e:
            print(f"Design suggestion error: {e}")
            return self._get_fallback_design_suggestions(room_type, style)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback responses when Gemini is unavailable"""
        return "I'm currently unable to generate a response. Please check your API key configuration."

    
    def _get_fallback_design_suggestions(self, room_type: str, style: str) -> Dict[str, Any]:
        """Fallback design suggestions"""
        return {
            "color_palette": ["#F8F6F0", "#9CA3AF", "#1E3A8A", "#D97706"],
            "furniture": [
                f"{style} sofa in neutral tones",
                f"Wooden coffee table with {style.lower()} design",
                f"Floor lamp with {style.lower()} aesthetic",
                "Area rug to define the space"
            ],
            "lighting": [
                "Natural light maximization",
                "Layered lighting with ambient and task lighting",
                "Warm LED bulbs for cozy atmosphere"
            ],
            "materials": [
                "Natural wood finishes",
                "Soft textiles for comfort",
                "Metal accents for contrast"
            ],
            "decor": [
                "Plants for natural elements",
                "Artwork that reflects personal style",
                "Throw pillows for color and texture"
            ]
        }

# Global Gemini client instance
gemini_client = GeminiClient()