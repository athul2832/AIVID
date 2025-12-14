import json
import base64
from typing import List, Dict, Any, Optional
from io import BytesIO
from PIL import Image
from gemini_client import gemini_client
from gemini_image_generator import gemini_image_generator

def generate_image_prompt(topic: str) -> Dict[str, Any]:
    """
    Generates a detailed image prompt from a simple topic.
    Corresponds to generate-image-prompt.ts flow.
    """
    if not gemini_client:
        raise Exception("LLM service is not available. Please check API key configuration.")
    
    prompt_text = f"""
    You are an expert interior designer and a skilled prompt engineer for text-to-image models. 
    Your task is to expand the given topic into a detailed, descriptive, and photorealistic prompt. 
    The prompt should be a single paragraph that captures the mood, materials, lighting, and key elements 
    of a professionally designed space.
    
    Return your response as a raw JSON object with the key "generatedPrompt".
    
    Topic: {topic}
    """
    
    try:
        response_text = gemini_client.generate_response(prompt_text)
        # Clean and parse the response
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        
        parsed = json.loads(cleaned_response)
        return {"generatedPrompt": parsed.get("generatedPrompt", "")}
    except Exception as e:
        raise Exception(f"Failed to generate image prompt: {str(e)}")

def generate_interior_design_from_prompt(prompt: str, design_style: str) -> Dict[str, Any]:
    """
    Generates interior design images based on a text prompt.
    Corresponds to generate-interior-design-from-prompt.ts flow.
    """
    if not gemini_image_generator:
        raise Exception("Image generator is not available. Please check API key configuration.")
    
    # Generate 4 images with civil engineer, architect, and designer perspective
    image_urls = []
    for _ in range(4):
        try:
            result = gemini_image_generator.generate_image(
                prompt=prompt,
                style=design_style,
                room_type="room",
                features="As a civil engineer, architect, and interior designer, ensure high quality, detailed, professional architectural visualization with realistic lighting, materials, and spatial planning. Consider structural elements, ergonomic design, and sustainable materials."
            )
            if result.get("image_urls"):
                image_urls.extend(result["image_urls"])
        except Exception as e:
            print(f"Warning: Failed to generate one of the images: {e}")
            continue
    
    if not image_urls:
        raise Exception("No images were generated.")
    
    return {"imageUrls": image_urls}

def edit_interior_design_with_text(base_image: str, edit_prompt: str, design_style: Optional[str] = None) -> Dict[str, Any]:
    """
    Edits an existing AI-generated interior design image using a text prompt.
    Corresponds to edit-interior-design-with-text.ts flow.
    """
    if not gemini_image_generator:
        raise Exception("Image generator is not available. Please check API key configuration.")
    
    # Decode the base64 image
    try:
        if base_image.startswith('data:image'):
            header, encoded = base_image.split(',', 1)
            image_bytes = base64.b64decode(encoded)
        else:
            image_bytes = base64.b64decode(base_image)
    except Exception as e:
        raise Exception(f"Failed to decode base image: {str(e)}")
    
    # Generate 4 edited images with civil engineer, architect, and designer perspective
    edited_images = []
    for _ in range(4):
        try:
            result = gemini_image_generator._generate_gemini_image_edit(
                prompt=f"As a civil engineer, architect, and interior designer, edit the provided image with the following instruction: {edit_prompt}. If a design style is provided, apply it: {design_style or 'not specified'}. Ensure realistic architectural visualization with proper structural considerations, ergonomic design, and sustainable materials.",
                image_data=image_bytes
            )
            # Convert bytes to data URI
            image_data_uri = f"data:image/png;base64,{base64.b64encode(result).decode()}"
            edited_images.append(image_data_uri)
        except Exception as e:
            print(f"Warning: Failed to generate one of the edited images: {e}")
            continue
    
    if not edited_images:
        raise Exception("No edited images were generated.")
    
    return {"editedImages": edited_images}

def get_design_suggestions_from_chat(query: str) -> Dict[str, Any]:
    """
    Gets design suggestions from chat query.
    Corresponds to get-design-suggestions-from-chat.ts flow.
    """
    if not gemini_client:
        raise Exception("LLM service is not available. Please check API key configuration.")
    
    prompt_text = f"""
    You are a helpful AI assistant specialized in interior design.
    The user is asking for design suggestions. Please provide a concise and helpful suggestion based on their query.
    
    Return your response as a raw JSON object with the key "suggestion".
    
    User Query: {query}
    """
    
    try:
        response_text = gemini_client.generate_response(prompt_text)
        # Clean and parse the response
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        
        parsed = json.loads(cleaned_response)
        return {"suggestion": parsed.get("suggestion", "")}
    except Exception as e:
        raise Exception(f"Failed to get design suggestions: {str(e)}")

def summarize_design_styles(design_styles: List[str]) -> Dict[str, Any]:
    """
    Summarizes a collection of design styles.
    Corresponds to summarize-design-styles.ts flow.
    """
    if not gemini_client:
        raise Exception("LLM service is not available. Please check API key configuration.")
    
    summaries = []
    for design_style in design_styles:
        try:
            prompt_text = f"""
            Summarize the key characteristics of the following design style in a single sentence. 
            Return your response as a raw JSON object with the key "summary".
            
            {design_style}
            """
            
            response_text = gemini_client.generate_response(prompt_text)
            # Clean and parse the response
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove ```
            
            parsed = json.loads(cleaned_response)
            summaries.append(parsed.get("summary", ""))
        except Exception as e:
            print(f"Warning: Failed to summarize design style {design_style}: {e}")
            summaries.append(f"Summary of {design_style} style.")
    
    return {"summaries": summaries}

def suggest_image_edits(base_image: str, design_style: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes an image and suggests a creative edit prompt.
    Corresponds to suggest-image-edits.ts flow.
    """
    if not gemini_client:
        raise Exception("LLM service is not available. Please check API key configuration.")
    
    prompt_text = f"""
    As a civil engineer, architect, and interior designer, analyze the provided image and suggest a creative edit.
    If a design style is provided, tailor the suggestion to that style.
    The suggestion should be a concise, actionable prompt for another AI to execute.
    Example: "Change the sofa to a velvet green one and add a gallery wall above it."
    
    Consider structural elements, ergonomic design, and sustainable materials in your suggestion.
    
    Return your response as a raw JSON object with the key "suggestion".
    
    Design Style: {design_style or "not specified"}
    """
    # Note: In a full implementation, we would pass the image to a multimodal model
    # For now, we'll generate a text-based suggestion without the actual image
    
    try:
        response_text = gemini_client.generate_response(prompt_text)
        # Clean and parse the response
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        
        parsed = json.loads(cleaned_response)
        return {"suggestion": parsed.get("suggestion", "")}
    except Exception as e:
        raise Exception(f"Failed to suggest image edits: {str(e)}")

def generate_image_from_cad_floor_plan(cad_floor_plan_data_uri: str, design_style: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates an interior design image from a CAD floor plan.
    Corresponds to generate-image-from-cad-floor-plan.ts flow.
    """
    if not gemini_image_generator:
        raise Exception("Image generator is not available. Please check API key configuration.")
    
    # Decode the base64 floor plan
    try:
        if cad_floor_plan_data_uri.startswith('data:image'):
            header, encoded = cad_floor_plan_data_uri.split(',', 1)
            image_bytes = base64.b64decode(encoded)
        else:
            image_bytes = base64.b64decode(cad_floor_plan_data_uri)
    except Exception as e:
        raise Exception(f"Failed to decode floor plan image: {str(e)}")
    
    # Generate 4 images based on the floor plan with civil engineer, architect, and designer perspective
    generated_image_urls = []
    for _ in range(4):
        try:
            result = gemini_image_generator._generate_gemini_image_edit(
                prompt=f"As a civil engineer, architect, and interior designer, interpret the attached floor plan and generate a photorealistic architectural visualization. The design should be in the style of {design_style}. Incorporate these additional details: {prompt or 'not specified'}. Ensure realistic architectural visualization with proper structural considerations, ergonomic design, and sustainable materials.",
                image_data=image_bytes
            )
            # Convert bytes to data URI
            image_data_uri = f"data:image/png;base64,{base64.b64encode(result).decode()}"
            generated_image_urls.append(image_data_uri)
        except Exception as e:
            print(f"Warning: Failed to generate one of the images from floor plan: {e}")
            continue
    
    if not generated_image_urls:
        raise Exception("No images were generated from the floor plan.")
    
    return {"generatedImageUrls": generated_image_urls}