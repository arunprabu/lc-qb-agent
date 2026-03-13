from fastapi import APIRouter
from app.services.tts_service import generate_speech

router = APIRouter()

@router.post("/playing")
async def playing_passage():
    # will have a passage text 
    my_passage = "Climate change refers to significant changes in global temperatures and weather patterns over time. While climate change is a natural phenomenon, human activities have been a major driver of recent changes. The burning of fossil fuels, deforestation, and industrial processes release greenhouse gases into the atmosphere, leading to a rise in global temperatures. This warming affects ecosystems and biodiversity, causing shifts in habitats and species distribution. Additionally, climate change results in more frequent and severe weather events, such as hurricanes, droughts, and floods. Mitigating climate change requires collective action, including reducing carbon emissions, transitioning to renewable energy sources, and promoting sustainable land use practices."

    # connecting to tts service to convert the passage to speech and play it in the frontend

    audio_response = await generate_speech(my_passage)
    print(f"Controller: Received audio response from TTS service: {audio_response}")

    return {
      "message": "Playing passage",
      "audio_url": audio_response
    }

    
