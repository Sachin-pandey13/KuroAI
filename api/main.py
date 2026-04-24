from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline.orchestrator import KuroAIOrchestrator
import uvicorn

app = FastAPI(title="KuroAI Backend")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with exact frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator globally
# This holds the Image models and LLM wrappers
orchestrator = KuroAIOrchestrator()

class AuthRequest(BaseModel):
    username: str
    password: str
    email: str = None

@app.post("/api/auth/signup")
async def signup(request: AuthRequest):
    return {"message": "User registered successfully!"}

@app.post("/api/auth/signin")
async def signin(request: AuthRequest):
    if not request.username or not request.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Return a mock JWT token and user info
    return {
        "token": "mock-jwt-token-12345",
        "username": request.username,
        "email": request.email or f"{request.username}@example.com"
    }

class GenerationRequest(BaseModel):
    story: str

@app.post("/api/generate")
async def generate_manga(request: GenerationRequest):
    try:
        # Run the full pipeline
        print(f"Generating manga for story: {request.story[:50]}...")
        result = orchestrator.run(request.story)
        return {
            "status": "success",
            "title": result.get("title"),
            "pages": result.get("images", []),
            "scenes": result.get("scenes", [])
        }
    except Exception as e:
        print(f"Generation error caught, serving fallback mock. Error: {str(e)}")
        
        # MOCK FALLBACK DATA 
        # When local models aren't running, this returns valid structure for the React Template Builder
        mock_scene_1 = _create_mock_base64_image(400, 300, "#2c3e50", "Scene 1: The Encounter")
        mock_scene_2 = _create_mock_base64_image(400, 300, "#8e44ad", "Scene 2: The Action")
        mock_scene_3 = _create_mock_base64_image(400, 600, "#c0392b", "Scene 3: The Resolution")
        
        return {
            "status": "success",
            "title": "Fallback Mock Story",
            "pages": [mock_scene_1, mock_scene_2, mock_scene_3],
            "scenes": [
                {
                    "dialogue": [
                        {"speaker": "Hero", "text": "Who goes there? I won't let you pass!"},
                        {"speaker": "Villain", "text": "Hah! You think you can stop me?"}
                    ]
                },
                {
                    "dialogue": [
                        {"speaker": "Hero", "text": "Take this! *Swing*"},
                        {"speaker": "Villain", "text": "Argh! Impossible!"}
                    ]
                },
                {
                    "dialogue": [
                        {"speaker": "Hero", "text": "It is finally over."},
                        {"speaker": "Narrator", "text": "And so peace returned to the valley."}
                    ]
                }
            ]
        }

def _create_mock_base64_image(width, height, color, text):
    try:
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        import base64
        
        img = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(img)
        draw.text((20, height // 2), text, fill="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"
    except Exception:
        return ""

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
