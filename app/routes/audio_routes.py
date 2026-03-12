# create an api endpoint to receive audio files and transcribe them using the whisper model

from fastapi import APIRouter, File, UploadFile
# from app.services.audio_service import AudioService

router = APIRouter()
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    print("Received file:", file.filename)
    # audio_service = AudioService()
    # transcription = await audio_service.transcribe_audio(file)
    return {"transcription": "will process soon"} 



