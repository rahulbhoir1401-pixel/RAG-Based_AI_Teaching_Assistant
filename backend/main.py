import os
import subprocess
import json
import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG Teaching Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).parent.parent
VIDEOS_DIR = ROOT_DIR / "Videos_test"
AUDIOS_DIR = ROOT_DIR / "1.converted_audios"
CHUNKS_DIR = ROOT_DIR / "2.jsons_chunks"

# Add ROOT_DIR to PATH so whisper and subprocesses can find ffmpeg.exe
os.environ["PATH"] += os.pathsep + str(ROOT_DIR)

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
VIDEOS_DIR.mkdir(exist_ok=True)
AUDIOS_DIR.mkdir(exist_ok=True)
CHUNKS_DIR.mkdir(exist_ok=True)

class ChatQuery(BaseModel):
    query: str
    top_k: int = 3

@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "llm_url": LLM_BASE_URL,
        "llm_model": LLM_MODEL,
        "embed_model": EMBED_MODEL
    }

@app.post("/api/upload")
async def upload_video(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.filename.endswith(".mp4"):
            raise HTTPException(status_code=400, detail="Only .mp4 files are supported.")
        
        file_path = VIDEOS_DIR / file.filename
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            results.append({"filename": file.filename, "status": "uploaded"})
        except Exception as e:
            logger.error(f"Failed to upload {file.filename}: {str(e)}")
            results.append({"filename": file.filename, "status": "failed", "error": str(e)})
            
    return {"uploads": results}

pipeline_status = {"status": "idle", "step": "Ready"}

@app.get("/api/process/status")
def get_process_status():
    return pipeline_status

@app.post("/api/process")
async def process_videos(background_tasks: BackgroundTasks):
    global pipeline_status
    if pipeline_status["status"] == "processing":
        return {"message": "Pipeline already running in the background."}

    pipeline_status = {"status": "processing", "step": "Starting pipeline..."}

    def run_pipeline():
        global pipeline_status
        try:
            pipeline_status["step"] = "1/4: Converting video to MP3 using ffmpeg..."
            logger.info("Starting pipeline step 1: process_video_to_mp3.py")
            subprocess.run(["python", "1.process_video_to_mp3.py"], cwd=str(ROOT_DIR), check=True)
            
            pipeline_status["step"] = "2/4: Transcribing audio with Whisper (This will take a while for large videos)..."
            logger.info("Starting pipeline step 2: create_chunks.py")
            subprocess.run(["python", "2.create_chunks.py"], cwd=str(ROOT_DIR), check=True)
            
            pipeline_status["step"] = "3/4: Creating vector embeddings via Ollama..."
            logger.info("Starting pipeline step 3: joblib_to_save_df.py (creates embeddings)")
            subprocess.run(["python", "5.joblib_to_save_df.py"], cwd=str(ROOT_DIR), check=True)
            
            pipeline_status["step"] = "4/4: Merging final chunks..."
            logger.info("Starting pipeline step 4: post-project_merge_chunks.py")
            subprocess.run(["python", "9.post-project_merge_chunks.py"], cwd=str(ROOT_DIR), check=True)
            
            pipeline_status["status"] = "success"
            pipeline_status["step"] = "Completed successfully!"
            logger.info("Pipeline completed successfully.")
        except subprocess.CalledProcessError as e:
            pipeline_status["status"] = "error"
            pipeline_status["step"] = f"Pipeline failed during {pipeline_status['step']}"
            logger.error(f"Pipeline step failed: {e}")
        except Exception as e:
            pipeline_status["status"] = "error"
            pipeline_status["step"] = f"Pipeline error: {str(e)}"
            logger.error(f"Pipeline error: {str(e)}")

    background_tasks.add_task(run_pipeline)
    return {"message": "Pipeline started in the background."}

def create_embedding(text_list):
    embeddings = []
    for text in text_list:
        if text is None or not str(text).strip():
            text = "empty content"
        try:
            r = requests.post(f"{LLM_BASE_URL}/api/embeddings", json={
                "model": EMBED_MODEL,
                "prompt": text
            })
            data = r.json()
            if "embedding" not in data:
                r = requests.post(f"{LLM_BASE_URL}/api/embeddings", json={
                    "model": EMBED_MODEL,
                    "prompt": "placeholder text"
                })
                data = r.json()
            embeddings.append(data["embedding"])
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            embeddings.append([0.0] * 1024) # fallback embedding shape for bgem3
    return embeddings

@app.post("/api/chat")
def chat(query: ChatQuery):
    joblib_path = ROOT_DIR / 'embeddings.joblib'
    if not joblib_path.exists():
        raise HTTPException(status_code=400, detail="Embeddings not found. Please run the processing pipeline first.")
        
    df = joblib.load(str(joblib_path))
    question_embedding = create_embedding([query.query])[0]
    
    similarities = cosine_similarity(np.vstack(df['embedding']), [question_embedding]).flatten()
    max_indx = (similarities.argsort()[::-1][:query.top_k])    
    
    new_df = df.loc[max_indx]
    
    prompt = f'''I am teaching basics of AI cource. Here are video subtitle chunks containing video title, video number, start time in seconds, end time in seconds, the text at that time:

{new_df[["title","number","start","end","text"]].to_json(orient="records")}
-------------------------
"{query.query}"
the user asked this question related to the video chunks, you have to answer in a human way(dont mention the above format, its just for you) where and how much content is taught in which video (in which video and what timestamp) and guide guide the user to go to that particular video. If user asks unrelated question, tell him that you can only ask questions related to the cource .
'''
    
    # Send to LLM
    try:
        r = requests.post(f"{LLM_BASE_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream" : False
        })
        response_data = r.json()
        llm_answer = response_data.get("response", "No response generated.")
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        llm_answer = "Error connecting to local LLM. Make sure Ollama is running."
        
    # Format chunks for UI
    retrieved_chunks = []
    for idx, row in new_df.iterrows():
        retrieved_chunks.append({
            "title": row.get("title", ""),
            "number": row.get("number", ""),
            "start": row.get("start", ""),
            "end": row.get("end", ""),
            "text": row.get("text", ""),
            "score": float(similarities[idx])
        })

    return {
        "answer": llm_answer,
        "chunks": retrieved_chunks,
        "prompt": prompt
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
