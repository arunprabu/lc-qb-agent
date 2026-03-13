from openai import AsyncOpenAI
from pathlib import Path
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_AUDIOS_DIR = Path("audios/output")

async def generate_speech(text: str, output_filename: str = "passage.mp3") -> dict:
    print(f"SERVICE: Generating speech for text: {text}")
    _AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = _AUDIOS_DIR / output_filename

    async with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        response_format="mp3",
    ) as response:
        await response.stream_to_file(output_path)

    print(f"SERVICE: Audio saved to {output_path}")
    return {
        "audio_url": str(output_path)
    }