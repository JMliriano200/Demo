from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
DID_API_KEY = os.getenv("DID_API_KEY", "")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
ELEVENLABS_BASE_URL = os.getenv("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io/v1")
DID_BASE_URL = os.getenv("DID_BASE_URL", "https://api.d-id.com")

SYSTEM_PROMPT = (
    "Eres un personaje empático y amable. Observa la escena con cuidado, "
    "describe lo que ves de manera positiva y responde a las preguntas del usuario "
    "con un tono cálido y cercano."
)

app = FastAPI(title="AI Avatar Prototype")


@dataclass
class AvatarResponse:
    text: str
    tts_audio_b64: str
    animation_url: str


def _require_env(value: str, name: str) -> None:
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")


def _encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def _openai_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }


def _elevenlabs_headers() -> dict[str, str]:
    return {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }


def _did_headers() -> dict[str, str]:
    return {
        "Authorization": f"Basic {DID_API_KEY}",
        "Content-Type": "application/json",
    }


def call_openai_vision(prompt: str, image_b64: str) -> str:
    _require_env(OPENAI_API_KEY, "OPENAI_API_KEY")

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ],
            },
        ],
        "temperature": 0.7,
    }

    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers=_openai_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"].strip()


def call_elevenlabs_tts(text: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL") -> str:
    _require_env(ELEVENLABS_API_KEY, "ELEVENLABS_API_KEY")

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}",
            headers=_elevenlabs_headers(),
            json=payload,
        )
        response.raise_for_status()
        audio_bytes = response.content

    return _encode_image_to_base64(audio_bytes)


def call_did_lipsync(image_url: str, audio_b64: str) -> str:
    _require_env(DID_API_KEY, "DID_API_KEY")

    payload = {
        "source_url": image_url,
        "script": {
            "type": "audio",
            "audio": audio_b64,
            "subtitles": False,
            "provider": {"type": "microsoft", "voice_id": "es-ES-AlvaroNeural"},
        },
    }

    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{DID_BASE_URL}/talks",
            headers=_did_headers(),
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data.get("result_url", "")


def build_avatar_response(
    prompt: str,
    camera_frame: bytes,
    character_image_url: str,
) -> AvatarResponse:
    frame_b64 = _encode_image_to_base64(camera_frame)
    response_text = call_openai_vision(prompt, frame_b64)
    tts_audio_b64 = call_elevenlabs_tts(response_text)
    animation_url = call_did_lipsync(character_image_url, tts_audio_b64)

    return AvatarResponse(
        text=response_text,
        tts_audio_b64=tts_audio_b64,
        animation_url=animation_url,
    )


@app.post("/avatar/respond")
async def respond(
    prompt: str,
    character_image_url: str,
    camera_frame: UploadFile = File(...),
) -> JSONResponse:
    camera_bytes = await camera_frame.read()
    result = build_avatar_response(prompt, camera_bytes, character_image_url)

    return JSONResponse(
        {
            "text": result.text,
            "tts_audio_b64": result.tts_audio_b64,
            "animation_url": result.animation_url,
        }
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
