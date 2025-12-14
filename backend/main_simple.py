import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
from datetime import datetime
import json
import random
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add the backend directory to sys.path to make imports work
import sys
from pathlib import Path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import AI components (with error handling for model issues)
try:
    from gemini_image_generator import gemini_image_generator as image_generator
    gemini_image_generator_available = True
    image_generator_available = True  # Make sure this variable is defined
except Exception as e:
    print(f"Image generator not available: {e}")
    image_generator = None
    gemini_image_generator_available = False
    image_generator_available = False

try:
    from gemini_client import gemini_client as llm_client
    gemini_llm_client_available = True
except Exception as e:
    print(f"Gemini client not available: {e}")
    llm_client = None
    gemini_llm_client_available = False

# Import config
from config import GENERATED_IMAGES_DIR
from gemini_flows import generate_image_prompt, generate_interior_design_from_prompt, edit_interior_design_with_text, get_design_suggestions_from_chat, summarize_design_styles, suggest_image_edits, generate_image_from_cad_floor_plan

# Ensure directories exist
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# FASTAPI APP SETUP
app = FastAPI()

# Add exception handler for validation errors
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    print(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": str(exc)}
    )

# Configure CORS to allow communication with the frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://localhost:9002", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:5178"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
# Check if frontend build exists
frontend_build_path = Path(__file__).parent.parent / "frontend" / ".next"
if frontend_build_path.exists():
    app.mount("/_next", StaticFiles(directory=str(frontend_build_path), html=True), name="nextjs")

# --- INPUT MODELS ---
class PromptRequest(BaseModel):
    style: str
    topic: Optional[str] = None # for prompt generation

class SummaryRequest(BaseModel):
    prompt: str
    style: str
    features: str
    
class SaveProjectRequest(BaseModel):
    user_id: str = "guest"
    project_name: str
    geometry_data: str
    final_image_url: str

class DesignGeneration(BaseModel):
    prompt: str
    style: str
    features: Optional[str] = None

class ChatMessage(BaseModel):
    query: str
    session_id: Optional[str] = None

class SuggestionRequest(BaseModel):
    baseImage: Optional[str] = None
    designStyle: Optional[str] = None

class GenerateImagePromptRequest(BaseModel):
    topic: str

class GenerateInteriorDesignRequest(BaseModel):
    prompt: str
    designStyle: str

class EditInteriorDesignRequest(BaseModel):
    baseImage: str
    editPrompt: str
    designStyle: Optional[str] = None

class GetDesignSuggestionsRequest(BaseModel):
    query: str

class SummarizeDesignStylesRequest(BaseModel):
    designStyles: List[str]

class SuggestImageEditsRequest(BaseModel):
    baseImage: str
    designStyle: Optional[str] = None

class GenerateImageFromCadFloorPlanRequest(BaseModel):
    cadFloorPlanDataUri: str
    designStyle: str
    prompt: Optional[str] = None

# --- DATABASE SIMULATION (In-memory for simple version) ---
projects_db = []
materials_db = [
    {"id": 1, "name": "Bamboo Flooring", "category": "Flooring", "eco_friendly": True, "price": 150},
    {"id": 2, "name": "Reclaimed Wood Desk", "category": "Furniture", "eco_friendly": True, "price": 800},
    {"id": 3, "name": "VOC-Free Paint", "category": "Paint", "eco_friendly": True, "price": 50},
    {"id": 4, "name": "Wool Rug", "category": "Flooring", "eco_friendly": False, "price": 450},
    {"id": 5, "name": "Recycled Glass Countertop", "category": "Surface", "eco_friendly": True, "price": 900},
]

# --- ENDPOINTS ---

@app.get("/")
async def read_root():
    # Check LLM status
    llm_status = "not accessible"
    llm_details = "No details"
    try:
        # Try to check if Gemini is accessible
        if 'llm_client' in globals() and llm_client is not None:
            llm_status = "running"
            # Test if the model is actually working
            try:
                test_response = llm_client.generate_response("Say hello world")
                llm_details = f"Model working: {test_response[:50]}..."
            except Exception as e:
                llm_details = f"Model initialization failed: {str(e)}"
    except Exception as e:
        llm_details = f"Global check failed: {str(e)}"
    
    return {
        "message": "AI Interior Design API is running with full AI capabilities!",
        "llm_status": llm_status,
        "llm_details": llm_details
    }

@app.get("/health")
async def health_check():
    ai_status = {
        "image_generator": gemini_image_generator_available or image_generator_available,
        "llm_client": gemini_llm_client_available,
        "llm_api": False
    }
    
    # Check if LLM API is accessible
    try:
        # Try to check if the LLM is accessible
        if 'llm_client' in globals() and llm_client is not None:
            ai_status["llm_api"] = True
    except:
        pass
    
    return {"status": "healthy", "ai_components": ai_status}

# --- IMAGE GENERATION ENDPOINT ---
@app.post("/generate-design")
async def generate_design(
    prompt: str = Form(...),
    style: str = Form(...),
    mode: str = Form(...), # 'text', 'image', 'floorplan'
    baseImage: Optional[str] = Form(None),
    floorPlan: Optional[str] = Form(None)
):
    """Generate interior design images based on user input"""
    print(f"Received request with mode: {mode}, prompt: {prompt}, style: {style}")
    
    # Check if image generator is available
    if not (gemini_image_generator_available or image_generator_available) or image_generator is None:
        raise HTTPException(status_code=500, detail="Image generator not available")
    
    try:
        image_bytes = None
        room_type = "room" # default
        
        if mode == 'image' and baseImage:
            # Handle base64 encoded image
            if isinstance(baseImage, str) and baseImage.startswith('data:image'):
                import base64
                # Extract the base64 data from data URI
                header, encoded = baseImage.split(',', 1)
                image_bytes = base64.b64decode(encoded)
            elif not isinstance(baseImage, str):  # Handle UploadFile
                image_bytes = await baseImage.read()
            room_type = "staged room"
        elif mode == 'floorplan' and floorPlan:
            # Handle base64 encoded floor plan
            if isinstance(floorPlan, str) and floorPlan.startswith('data:image'):
                import base64
                # Extract the base64 data from data URI
                header, encoded = floorPlan.split(',', 1)
                image_bytes = base64.b64decode(encoded)
            elif not isinstance(floorPlan, str):  # Handle UploadFile
                image_bytes = await floorPlan.read()
            room_type = "floor plan based"
            
        print("Calling image generator...")
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        def run_image_generation():
            # Use the actual image generator
            if image_generator is not None:
                try:
                    result = image_generator.generate_image(
                        prompt=prompt,
                        style=style,
                        room_type=room_type,
                        features=prompt,  # passing prompt as features
                        image_file=image_bytes
                    )
                    return {
                        "success": True, 
                        "data": result["image_urls"],
                        "prompt": result.get("prompt", prompt),
                        "final_prompt": result.get("final_prompt", ""),
                        "image_ids": result.get("image_ids", [])
                    }
                except Exception as e:
                    print(f"Image generation failed: {e}")
                    # Re-raise the exception instead of using placeholder images
                    raise e
            else:
                # Raise exception if generator is not available
                raise Exception("Image generator is not available")

        # Use a thread pool executor to run the blocking image generation
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, run_image_generation)
        
        print(f"Image generator result: {result}")
        
        if result["success"]:
            return { 
                "data": result.get("data"),
                "prompt": result.get("prompt", ""),
                "final_prompt": result.get("final_prompt", ""),
                "image_ids": result.get("image_ids", [])
            }
        else:
            error_msg = result.get("error", "Unknown error occurred during image generation")
            raise HTTPException(status_code=500, detail=error_msg)
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error in generate_design: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# --- PROJECT MANAGEMENT ENDPOINTS ---
@app.get("/projects")
async def get_projects():
    """Get all projects (simplified version)"""
    return projects_db

@app.post("/save-project")
async def save_project(project_data: SaveProjectRequest):
    """Save a project to the database"""
    try:
        project = {
            "id": len(projects_db) + 1,
            "user_id": project_data.user_id,
            "project_name": project_data.project_name,
            "geometry_data": project_data.geometry_data,
            "final_image_url": project_data.final_image_url,
            "created_at": datetime.now().isoformat()
        }
        projects_db.append(project)
        return {"message": "Project saved successfully!", "project_id": project["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save project: {str(e)}")

# --- RECOMMENDATION ENDPOINTS ---
@app.get("/get-recommendations/{style}")
async def get_recommendations(style: str):
    """Get material recommendations based on style"""
    try:
        # This is a mock implementation.
        summaries = {
            "Modern": "Characterized by clean lines, simple color palettes, and the use of materials like metal, glass, and steel.",
            "Minimalist": "A style that is simple, uncluttered, and monochromatic, emphasizing functionality.",
            "Scandinavian": "Combines beauty, simplicity and functionality with natural elements like light wood and plants.",
            "Bohemian": "A free-spirited aesthetic that mixes different cultures and artistic expressions into an eclectic style.",
            "Industrial": "An aesthetic trend that takes clues from old factories and industrial spaces.",
            "Coastal": "A beach-inspired design that uses light colors, natural materials, and a relaxed feel."
        }
        num_styles = len(style.split(',')) if style else 0
        return {"data": list(summaries.values())[:num_styles] if num_styles > 0 else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@app.post("/generate-new-prompt")
async def generate_new_prompt(request: PromptRequest):
    """Generate a creative prompt based on the selected style"""
    # Check if LLM client is available
    print(f"LLM client available: {llm_client is not None}")
    if not llm_client:
        print("LLM client is None, raising HTTP 503")
        raise HTTPException(status_code=503, detail="LLM service is not available. Please check API key configuration.")
    
    try:
        prompt_text = (
            f"You are a creative interior designer. Your task is to generate a short, creative "
            f"design prompt for a {request.style} {request.topic}. The prompt should be a sentence or two "
            f"describing the room's core elements and atmosphere. Respond only with the prompt text. Do not use quotes."
        )
        print(f"Generating prompt with text: {prompt_text}")
        new_prompt = llm_client.generate_response(prompt_text)
        print(f"Generated prompt: {new_prompt}")
        return {"success": True, "data": new_prompt}
    except Exception as e:
        print(f"Error generating prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate prompt: {str(e)}")


@app.post("/suggest-edits")
async def suggest_edits(request: SuggestionRequest):
    """Suggest edits for a given image."""
    # Check if LLM client is available
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM service is not available. Please check API key configuration.")

    try:
        # In a real app, we would pass the image data to a multimodal model.
        # Here we simulate it with a text prompt.
        prompt = (
            f"You are an expert interior designer AI. Suggest a creative edit for an interior design image. "
            f"The current style is {request.designStyle}. The suggestion should be a concise, actionable prompt for another AI to execute. "
            f"Example: 'Change the sofa to a velvet green one and add a gallery wall above it.' Respond only with the suggestion."
        )
        suggestion = llm_client.generate_response(prompt)
        return {"data": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest edits: {str(e)}")

# --- FLOW ENDPOINTS ---
@app.post("/flow/generate-image-prompt")
async def flow_generate_image_prompt(request: GenerateImagePromptRequest):
    """Generate a detailed image prompt from a simple topic"""
    try:
        result = generate_image_prompt(request.topic)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image prompt: {str(e)}")

@app.post("/flow/generate-interior-design-from-prompt")
async def flow_generate_interior_design_from_prompt(request: GenerateInteriorDesignRequest):
    """Generate interior design images based on a text prompt"""
    try:
        result = generate_interior_design_from_prompt(request.prompt, request.designStyle)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate interior design: {str(e)}")

@app.post("/flow/edit-interior-design-with-text")
async def flow_edit_interior_design_with_text(request: EditInteriorDesignRequest):
    """Edit an existing AI-generated interior design image using a text prompt"""
    try:
        result = edit_interior_design_with_text(request.baseImage, request.editPrompt, request.designStyle)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to edit interior design: {str(e)}")

@app.post("/flow/get-design-suggestions-from-chat")
async def flow_get_design_suggestions_from_chat(request: GetDesignSuggestionsRequest):
    """Get design suggestions from chat query"""
    try:
        result = get_design_suggestions_from_chat(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get design suggestions: {str(e)}")

@app.post("/flow/summarize-design-styles")
async def flow_summarize_design_styles(request: SummarizeDesignStylesRequest):
    """Summarize a collection of design styles"""
    try:
        result = summarize_design_styles(request.designStyles)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize design styles: {str(e)}")

@app.post("/flow/suggest-image-edits")
async def flow_suggest_image_edits(request: SuggestImageEditsRequest):
    """Analyze an image and suggest a creative edit prompt"""
    try:
        result = suggest_image_edits(request.baseImage, request.designStyle)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suggest image edits: {str(e)}")

@app.post("/flow/generate-image-from-cad-floor-plan")
async def flow_generate_image_from_cad_floor_plan(request: GenerateImageFromCadFloorPlanRequest):
    """Generate an interior design image from a CAD floor plan"""
    try:
        result = generate_image_from_cad_floor_plan(request.cadFloorPlanDataUri, request.designStyle, request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image from CAD floor plan: {str(e)}")

# --- CHAT ENDPOINT ---
@app.post("/chat")
async def chat(message: ChatMessage):
    """Handle chat messages with the AI assistant"""
    # Check if LLM client is available
    if not llm_client:
        raise HTTPException(status_code=503, detail="LLM service is not available. Please check API key configuration.")
    
    try:
        context = [{"role": "user", "content": message.query}]
        response = llm_client.generate_response(message.query, context)
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Server startup code
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)