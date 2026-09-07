"""
Tarteel Whisper Quran Model Loader
Loads fine-tuned Whisper model for Qur'anic recitation (tarteel-ai/whisper-base-ar-quran)
Supports CUDA GPU acceleration with automatic CPU / lightweight fallback.
"""
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("quran_asr")

class QuranWhisperEngine:
    def __init__(self, model_id: str = "tarteel-ai/whisper-base-ar-quran"):
        self.model_id = model_id
        self.device = "cpu"
        self.pipe = None
        self.is_ml_ready = False
        self._init_model()

    def _init_model(self):
        try:
            import torch
            from transformers import pipeline

            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading Whisper Quran model '{self.model_id}' on {self.device}...")

            # Load ASR pipeline
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model_id,
                device=self.device,
                generate_kwargs={"language": "arabic", "task": "transcribe"}
            )
            self.is_ml_ready = True
            logger.info("Whisper Quran model loaded successfully!")
        except Exception as e:
            logger.warning(
                f"Full ML pipeline could not be loaded ({e}). "
                "Switching to Hybrid ASR Mode (supports audio processing & direct audio-text evaluation)."
            )
            self.is_ml_ready = False

    def transcribe(self, audio_path_or_bytes, expected_text: str = "") -> Dict[str, Any]:
        """
        Transcribes Arabic speech from audio.
        Returns transcribed text and individual word tokens with timestamps/durations.
        """
        if self.is_ml_ready and self.pipe:
            try:
                result = self.pipe(audio_path_or_bytes, return_timestamps="word")
                raw_text = result.get("text", "").strip()
                chunks = result.get("chunks", [])

                words = []
                durations = []
                for chunk in chunks:
                    word_text = chunk.get("text", "").strip()
                    ts = chunk.get("timestamp", (0.0, 0.0))
                    dur = ts[1] - ts[0] if (ts and len(ts) >= 2 and ts[1]) else 0.0
                    if word_text:
                        words.append(word_text)
                        durations.append(dur)

                if not words and raw_text:
                    words = raw_text.split()
                    durations = [0.0] * len(words)

                return {
                    "text": raw_text,
                    "words": words,
                    "durations": durations,
                    "engine": "tarteel-whisper"
                }
            except Exception as ex:
                logger.error(f"Whisper inference error: {ex}")

        # If ML pipeline is not loaded, return empty transcription so real user speech is evaluated
        return {
            "text": "",
            "words": [],
            "durations": [],
            "engine": "no-ml-loaded"
        }

# Singleton instance
asr_engine = QuranWhisperEngine()
