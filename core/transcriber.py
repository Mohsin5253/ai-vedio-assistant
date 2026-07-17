import whisper
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")
_model = None

def load_model():
    global _model
    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        # Added device="mps" here for faster Mac processing based on your previous logs!
        _model = whisper.load_model(WHISPER_MODEL, device="mps")
        print("Whisper model loaded.")
    return _model

def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    model = load_model()
    lang = language.lower()

    if lang in ["hindi", "hinglish"]:
        # By setting language="hi" and task="translate", you force Whisper 
        # to listen for Hindi/Hinglish and output ONLY English text.
        result = model.transcribe(
            chunk_path, 
            language="hi", 
            task="translate", 
            fp16=False
        )
    else:
        # Standard English transcription
        result = model.transcribe(
            chunk_path, 
            language="en", 
            task="transcribe", 
            fp16=False
        )

    return result["text"]

def transcribe_all(chunks: list, language: str = "english") -> str:
    full_transcript = ""
    print(f"Using Whisper for transcription (Mode: {language}).")
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, language=language)
        full_transcript += text + " "
    print("Transcription complete.")
    return full_transcript.strip()