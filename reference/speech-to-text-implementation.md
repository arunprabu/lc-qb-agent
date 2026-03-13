# Speech-to-Text: Transcribe API — Step-by-Step Explanation

This document walks through every layer of the `/api/v1/audio/transcribe` endpoint,
from HTTP request to JSON response.

---

## Architecture Overview

```
Client (POST /api/v1/audio/transcribe)
        │
        ▼
  app/main.py          ← FastAPI app; mounts the audio router at /api/v1/audio
        │
        ▼
  app/routes/audio_routes.py   ← Defines the POST /transcribe endpoint
        │
        ▼
  app/services/audio_service.py  ← Core transcription logic using Whisper
        │
        ▼
  OpenAI Whisper (local model)   ← Performs the actual speech-to-text
```

---

## Step 1 — App Bootstrap (`app/main.py`)

```python
app = FastAPI(title="Question Bank Agent", version="1.0")
app.include_router(audio_router, prefix="/api/v1/audio")
```

When the server starts, FastAPI registers the `audio_router` under the prefix
`/api/v1/audio`. Any route defined inside `audio_routes.py` will be reachable
at `/api/v1/audio/<route-path>`.

---

## Step 2 — Whisper Model Pre-Load (`app/services/audio_service.py`)

```python
model = whisper.load_model("base")
```

This line runs **once at module import time** — not on every request.  
Loading a Whisper model takes several seconds and consumes significant memory,
so doing it once at startup keeps individual requests fast.

Available model sizes (speed ↔ accuracy tradeoff):

| Model  | Speed   | Accuracy |
| ------ | ------- | -------- |
| tiny   | fastest | lowest   |
| base   | fast    | good     |
| small  | medium  | better   |
| medium | slow    | high     |
| large  | slowest | best     |
| turbo  | fast    | high     |

---

## Step 3 — HTTP Endpoint (`app/routes/audio_routes.py`)

```python
@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
```

- **Method**: `POST`
- **Full URL**: `POST /api/v1/audio/transcribe`
- **Parameter**: `file` — a multipart form-data upload (`UploadFile`).  
  `File(...)` marks it as **required**; the request will be rejected with `422`
  if no file is provided.

The handler immediately delegates to `AudioService` and returns the result
dictionary as JSON.

---

## Step 4 — Service Layer (`app/services/audio_service.py`)

### 4a. Extract the file extension

```python
suffix = os.path.splitext(file.filename or "audio.mp3")[-1] or ".mp3"
```

Whisper infers the audio codec from the file extension (e.g. `.mp3`, `.wav`,
`.m4a`).

- `file.filename` may be `None` if the client omits it, so `"audio.mp3"` is
  used as a fallback.
- `os.path.splitext` splits `"recording.mp3"` → `("recording", ".mp3")`;
  `[-1]` picks the extension.
- A final `or ".mp3"` guards against files with no extension at all.

### 4b. Save to a temporary file

```python
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    contents = await file.read()
    tmp.write(contents)
    tmp_path = tmp.name
```

Whisper's `transcribe()` API accepts a **file path**, not an in-memory buffer.
The uploaded bytes must therefore be written to disk first.

Key details:

- `delete=False` — keeps the temp file alive after the `with` block closes the
  file handle, so Whisper can still open it by path.
- `await file.read()` — reads the entire upload into memory asynchronously
  (safe for audio files up to a few hundred MB).
- `tmp.name` — the OS-assigned absolute path to the temp file
  (e.g. `/tmp/tmpXyz123.mp3`).

### 4c. Run Whisper transcription

```python
result = model.transcribe(tmp_path)
```

Whisper loads the audio from disk, runs its encoder-decoder neural network,
and returns a dictionary. The two fields we use:

| Field                | Description                                 |
| -------------------- | ------------------------------------------- |
| `result["text"]`     | Full transcript as a single string          |
| `result["language"]` | BCP-47 language code detected (e.g. `"en"`) |

### 4d. Cleanup in `finally`

```python
finally:
    os.unlink(tmp_path)
```

`finally` ensures the temp file is **always deleted** — even if Whisper raises
an exception. This prevents disk accumulation across repeated requests.

---

## Step 5 — Response

The endpoint returns a plain JSON object:

```json
{
  "transcript": "Hello, this is a test recording.",
  "language": "en"
}
```

FastAPI automatically serialises the Python `dict` to JSON with a
`Content-Type: application/json` header.

---

## End-to-End Request Flow Summary

| #   | Layer   | What happens                                                       |
| --- | ------- | ------------------------------------------------------------------ |
| 1   | Client  | Sends `POST /api/v1/audio/transcribe` with audio file as form-data |
| 2   | FastAPI | Parses multipart body; creates `UploadFile` object                 |
| 3   | Route   | Calls `AudioService().transcribe_audio(file)`                      |
| 4   | Service | Detects extension; writes bytes to a temp file                     |
| 5   | Whisper | Loads audio from disk, runs speech-to-text inference               |
| 6   | Service | Extracts `text` and `language` from Whisper output                 |
| 7   | Cleanup | Temp file deleted in `finally` block                               |
| 8   | Route   | Returns `{"transcript": "...", "language": "..."}` as JSON         |

---

## How to Test

Using `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/audio/transcribe \
  -F "file=@/path/to/audio.mp3"
```

Using the interactive docs:

```
http://127.0.0.1:8000/docs  →  POST /api/v1/audio/transcribe
```
