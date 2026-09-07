"""
FastAPI ASR & Tajweed Alignment Microservice
"""
import os
import tempfile
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from asr_service.model_loader import asr_engine
    from asr_service.alignment import align_words, compute_overall_score
except ImportError:
    from model_loader import asr_engine
    from alignment import align_words, compute_overall_score

app = FastAPI(
    title="Quran Recitation ASR & Tajweed Service",
    version="1.0.0",
    description="Tarteel Whisper ASR + Forced Alignment + Rule-based Tajweed Verifier"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvaluationRequest(BaseModel):
    expected_text: str
    spoken_text: Optional[str] = None

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Quran ASR & Tajweed Microservice",
        "ml_ready": asr_engine.is_ml_ready,
        "device": asr_engine.device,
        "model_id": asr_engine.model_id
    }

@app.post("/evaluate-recitation")
async def evaluate_recitation(
    expected_text: str = Form(...),
    audio_file: Optional[UploadFile] = File(None),
    spoken_text: Optional[str] = Form(None)
):
    """
    Evaluates Quranic recitation from either an uploaded audio file or transcribed text.
    Performs word-level forced alignment and checks Tajweed rules.
    """
    expected_words = expected_text.strip().split()
    if not expected_words:
        raise HTTPException(status_code=400, detail="expected_text cannot be empty")

    spoken_words = []
    durations = []
    engine_used = "direct-text"

    # Step 1: Process Audio if uploaded
    if audio_file:
        suffix = os.path.splitext(audio_file.filename or "recitation.wav")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await audio_file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            transcription = asr_engine.transcribe(tmp_path, expected_text=expected_text)
            spoken_words = transcription["words"]
            durations = transcription["durations"]
            engine_used = transcription["engine"]
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    elif spoken_text:
        spoken_words = spoken_text.strip().split()
        durations = [0.4] * len(spoken_words)
    else:
        raise HTTPException(status_code=400, detail="Either audio_file or spoken_text must be provided")

    # Step 2: Perform Forced Alignment & Tajweed checking
    aligned_results = align_words(expected_words, spoken_words, durations)

    # Step 3: Compute Overall Score & Feedback
    summary = compute_overall_score(aligned_results)

    return {
        "success": True,
        "score": summary["score"],
        "correct_count": summary["correct_count"],
        "tajweed_issue_count": summary["tajweed_issue_count"],
        "incorrect_count": summary["incorrect_count"],
        "total_words": summary["total_words"],
        "overall_feedback": summary["feedback"],
        "aligned_words": aligned_results,
        "engine": engine_used
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
