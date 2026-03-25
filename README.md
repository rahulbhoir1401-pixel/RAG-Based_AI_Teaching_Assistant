<<<<<<< HEAD
# RAG-Based AI Teaching Assistant

A full-stack application that wraps a local RAG (Retrieval-Augmented Generation) pipeline for an AI teaching assistant. It allows users to upload educational videos, process them into transcripts and vector embeddings, and then chat with an AI assistant to fetch information directly mapped to specific timestamps in the videos.

## Requirements
- Python 3.10+
- Node.js 18+
- [FFmpeg](https://ffmpeg.org/download.html) (must be installed and available in system PATH)
- [Ollama](https://ollama.com/) (running locally)

## Models Needed
You must pull the required models in Ollama before running the app:
```bash
ollama pull llama3.2
ollama pull bge-m3
```

## First Setup

1. **Install Backend Dependencies**
```bash
pip install -r backend/requirements.txt
```
*(Note: `whisper` may require git: `pip install git+https://github.com/openai/whisper.git`)*

2. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

3. **Environment Setup**
Copy `.env.example` to `backend/.env` (or project root) and configure local endpoints if using something other than local Ollama.

## Running the Application

### Start the Backend
```bash
cd backend
python main.py
```
*The API will start at http://localhost:8000*

### Start the Frontend
```bash
cd frontend
npm run dev
```
*The UI will start at http://localhost:5173*

## How to use
1. Open the frontend UI in your browser.
2. Go to the Upload section and upload a `.mp4` video.
3. Click "Process Videos" to extract audio, generate transcription chunks, and build the vector embeddings.
4. Once completed, go to the Chat interface and ask questions about the video content.
=======
# RAG-Based_AI_Teaching_Assistant
🎓 RAG-Based AI Teaching Assistant  An intelligent full-stack application that transforms educational videos into a searchable knowledge base using a Retrieval-Augmented Generation (RAG) pipeline. Instead of manually watching long videos, users can ask questions and receive accurate, context-aware answers instantly.
>>>>>>> c00511f3aa971cf44ea72c6e23c2adb7cb2c9a62
