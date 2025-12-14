
# AIVID

AIVID is an AI-powered interior design studio that combines a Next.js frontend (TypeScript/React) with a Python FastAPI backend to generate, edit, and iterate on interior design images and chat-driven design guidance using Google Gemini models.

---

## Key Features
- Design generation from text prompts (multiple variations)
- Image editing of user-supplied photos by text instruction
- Interactive AI design chat assistant
- Style presets (Modern, Scandinavian, Industrial, etc.)
- Thumbnail generation and image management for fast UI rendering
- Graceful fallback and dual API-key support for reliability

---

## AI / ML Algorithms & Models

1. Google Gemini Models
- Text Generation: `googleai/gemini-2.5-flash` (design prompts, chat responses, suggestions)
- Image Generation: `googleai/gemini-2.5-flash-image` (create interior design images)
- Image Editing: `models/gemini-2.5-flash-image-preview` (modify existing images)

2. Prompt Engineering
- Role-Based Prompting: prompts include roles (e.g., "civil engineer, architect, interior designer") to steer outputs.
- Chain-of-Thought Reasoning: multi-step prompts to consider structural, ergonomic, and sustainable design aspects.
- Variation Generation: prompt variations to produce diverse outputs for the same user request.

3. Image Processing
- Thumbnail generation via PIL for fast previews.
- Consistent resizing using PIL's thumbnail/resize utilities.
- Base64 encoding/decoding for image transport in the API.
- Format conversion and metadata preservation on save (PNG/JPEG).

4. System & Backend Algorithms
- FastAPI routing for REST endpoints and static file serving.
- Concurrent processing using ThreadPoolExecutor to offload blocking Gemini/image I/O.
- Async/await patterns to keep event loop responsive.
- Error handling with retry/fallback for primary/backup API keys.
- Basic in-memory storage (list-based) for ephemeral project data and filesystem-based image persistence and cleanup.

5. UI/UX Algorithms
- React state management with useState/useEffect and React Hook Form.
- Zod schemas for validation and robust client-side form checking.

---

## Architecture

Frontend (Next.js — TypeScript)
- Main entry: `src/app/page.tsx` (renders `MainLayout`)
- Studio: `src/components/app/studio.tsx`
- Generation Panel: `src/components/app/generation-panel.tsx`
- Image Editor: `src/components/app/image-editor.tsx`
- Design Chat: `src/components/app/design-chat.tsx`

Backend (Python — FastAPI)
- Server: `backend/server.py`
- Image generator: `backend/gemini_image_generator.py`
- Text AI client: `backend/gemini_client.py`
- High-level flows: `backend/gemini_flows.py`
- Configuration: `backend/config.py`
- Generated images directory: `backend/generated_images/`

Full flow:
1. Start frontend (port 3000) and backend (port 8000).
2. User creates a design request via the Studio UI (text prompt + style).
3. Frontend calls `/generate-design` → backend uses Gemini image model to produce 4 variations, saves them to `backend/generated_images/`, generates thumbnails, returns URLs.
4. User may edit an image → frontend sends image + edit prompt to `/edit-image` → backend uses Gemini image-edit model to return edited image(s).
5. Chat interactions use `/chat` → backend uses Gemini text model to respond.

---

## Quick Start

Requirements
- Node.js 18+
- pnpm or npm
- Python 3.9+
- ffmpeg (optional but recommended for advanced video/image operations)
- Gemini API keys (primary + backup recommended)

Clone
git clone https://github.com/athul2832/AIVID.git
cd AIVID

Frontend
cd frontend (or root if monorepo)
pnpm install        # or npm install
pnpm run dev        # starts Next.js on http://localhost:3000

Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload

All-in-one (dev)
Use the provided start scripts:
- Unix: ./start.sh
- Windows: start.bat
npm run dev:full   # runs both frontend and backend concurrently (adjust to actual scripts)

---

## Environment Variables (example)
Create `.env` at project root or `backend/.env` with:
GEMINI_API_KEY_PRIMARY=sk-...
GEMINI_API_KEY_BACKUP=sk-...
BACKEND_PORT=8000
FRONTEND_PORT=3000
GENERATED_IMAGES_DIR=backend/generated_images
NODE_ENV=development

Note: The repo supports a dual-key fallback mechanism; set both keys for higher reliability.

---

## API Endpoints (examples)

POST /generate-design
- Description: Generate multiple design variations from a text prompt.
- Body (application/json):
  {
    "prompt": "Cozy Scandinavian living room with natural wood and light tones",
    "style": "Scandinavian",
    "num_variations": 4,
    "width": 1024,
    "height": 768
  }
- Response:
  { "images": ["url1", "url2", "url3", "url4"], "thumbnails": [...] }

POST /edit-image
- Description: Edit an uploaded image with text instructions.
- Body: multipart/form-data with `image` (file or base64) and `edit_prompt`
- Response: edited image URLs / base64 payload

POST /chat
- Description: Chat with the AI design assistant
- Body:
  { "message": "How can I make a small living room feel bigger?" }
- Response:
  { "reply": "..." }

GET /health
- Description: Service health check

Example curl:
curl -X POST "http://localhost:8000/generate-design" -H "Content-Type: application/json" -d '{"prompt":"modern loft","style":"Modern","num_variations":4}'

---

## File Structure (high level)
- src/                         — Next.js TypeScript app
  - app/page.tsx
  - components/app/*.tsx
- backend/
  - server.py
  - gemini_image_generator.py
  - gemini_client.py
  - gemini_flows.py
  - config.py
  - generated_images/
- scripts/                     — utility and start scripts
- requirements.txt
- package.json
- README.md

---

## Development Notes & Best Practices
- Thumbnails are created by backend to speed up UI load times; use thumbnails for gallery views.
- Long-running image generation runs on thread pool workers so the FastAPI event loop remains responsive.
- Use Zod + React Hook Form for adding new forms to keep frontend validation consistent.
- When adding new Gemini flows, centralize prompt templates in `gemini_flows.py` and preserve role-based prompt patterns.

---

## Contributing
- Open issues to discuss major features or breaking changes.
- Fork the repo, create a featurename branch, submit PRs with tests where applicable.
- Follow existing TypeScript linting and Python formatting rules.

---

## Troubleshooting
- If image generation fails, check both GEMINI API keys and network connectivity.
- Inspect backend logs for stack traces; retry may succeed via backup API key.
- Ensure `backend/generated_images/` is writable by the server process.

---

## License
Add your license of choice (e.g., MIT). Replace this section with the chosen license file.

---

Notes / Next steps
- Replace placeholder commands if package.json or script names differ.
- Add CI badges, usage screenshots, and a demo GIF for onboarding.
- Consider adding automated cleanup cron for guest images and rate-limiting for API endpoints.
