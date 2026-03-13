from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io

from app.services.tts_service import generate_speech

router = APIRouter()

@router.post("/playing")
async def playing_passage():

    my_passage = """
    Climate change refers to significant changes in global temperatures and weather patterns over time.
    While climate change is a natural phenomenon, human activities have been a major driver of recent changes.
    The burning of fossil fuels, deforestation, and industrial processes release greenhouse gases into the atmosphere.
    """

    audio_bytes = await generate_speech(my_passage)

    audio_stream = io.BytesIO(audio_bytes)

    return StreamingResponse(
        audio_stream,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=passage.mp3"}
    )