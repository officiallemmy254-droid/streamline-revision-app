from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
import asyncio
from notebooklm import NotebookLMClient
from . import auth

router = APIRouter(prefix="/notebooklm", tags=["NotebookLM"])

class NotebookCreateRequest(BaseModel):
    title: str

class ChatRequest(BaseModel):
    notebook_id: str
    message: str

class AudioOverviewRequest(BaseModel):
    notebook_id: str

@router.get("/status")
async def get_status():
    try:
        async with await NotebookLMClient.from_storage() as client:
            return {"status": "authenticated"}
    except Exception as e:
        return {"status": "unauthenticated", "error": str(e)}

@router.post("/notebooks")
async def create_notebook(req: NotebookCreateRequest, current_user: str = Depends(auth.get_current_user)):
    try:
        async with await NotebookLMClient.from_storage() as client:
            nb = await client.notebooks.create(req.title)
            return {"notebook_id": nb.id, "title": nb.title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notebooks/{notebook_id}/sources")
async def add_source(notebook_id: str, file: UploadFile = File(...), current_user: str = Depends(auth.get_current_user)):
    file_bytes = await file.read()
    temp_path = f"/tmp/{file.filename}"
    import os
    # Ensure /tmp exists on Windows? Better to use tempfile
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        async with await NotebookLMClient.from_storage() as client:
            await client.sources.add_file(notebook_id, tmp_path)
            return {"message": "Source added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/notebooks/chat")
async def chat_notebook(req: ChatRequest, current_user: str = Depends(auth.get_current_user)):
    try:
        async with await NotebookLMClient.from_storage() as client:
            response = await client.chat.ask(req.notebook_id, req.message)
            return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notebooks/audio")
async def generate_audio(req: AudioOverviewRequest, current_user: str = Depends(auth.get_current_user)):
    try:
        async with await NotebookLMClient.from_storage() as client:
            # Generate audio overview (podcast) for the notebook
            status = await client.artifacts.generate_audio(req.notebook_id)
            # Wait for completion and get the result
            await client.artifacts.wait_for_completion(req.notebook_id, status.task_id)
            # Get the generated audio
            audio_data = await client.artifacts.download_audio(req.notebook_id, status.task_id)
            return {"message": "Audio generation completed", "data": audio_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
