# AIVID

AIVID is an AI-powered interior design studio combining a Next.js (TypeScript) frontend with a Python (FastAPI) backend to generate, edit, and chat about interior designs using Google Gemini models.

## Architecture
- Frontend (Next.js, TypeScript)
  - Entry: src/app/page.tsx
  - Key components: src/components/app/studio.tsx, generation-panel.tsx, image-editor.tsx, design-chat.tsx
  - Dev port: 3000
- Backend (FastAPI, Python)
  - Core modules: backend/server.py, backend/gemini_image_generator.py, backend/gemini_client.py, backend/gemini_flows.py, backend/config.py
  - Generated images: backend/generated_images/
  - Dev port: 8000

## Models
- Text generation: googleai/gemini-2.5-flash
- Image generation: googleai/gemini-2.5-flash-image
- Image editing: models/gemini-2.5-flash-image-preview

The project uses prompt-engineering patterns (role-based prompts, chain-of-thought, variation generation) and basic image processing (thumbnails, resizing, base64 transport).

## Quick Usage
Requirements: Node.js 18+, Python 3.9+, Gemini API keys (primary + backup). Optional: ffmpeg.

Clone:
```
git clone https://github.com/athul2832/AIVID.git
cd AIVID
```

Frontend:
```
pm install    # or pnpm install
npm run dev    # starts Next.js on http://localhost:3000
```

Backend:
```
cd backend
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

Key API endpoints: POST /generate-design, POST /edit-image, POST /chat, GET /health

For more details (architecture, algorithms, implementation notes) see Info.md in the repository.
