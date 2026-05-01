"""AI প্রোভাইডার (টেক্সট ও ইমেজ)।

টেক্সট:
  - google : Google AI Studio (Gemini)
  - openrouter : OpenRouter (OpenAI-compatible)
  - custom : যেকোনো OpenAI-compatible endpoint

ইমেজ:
  - ghostweb : infip.pro endpoint
  - pollinations : pollinations.ai (free)
  - none : ইমেজ ছাড়া
"""

from __future__ import annotations

import logging
import urllib.parse

import httpx

from utils import sanitize_html

log = logging.getLogger(__name__)


SYSTEM_RULES = (
    "তুমি একজন অভিজ্ঞ বাংলা কনটেন্ট রাইটার। "
    "প্রতিটি পোস্ট অবশ্যই বাংলায় হবে এবং নিচের HTML ট্যাগ ছাড়া অন্য কোনো "
    "ফরম্যাটিং ব্যবহার করা যাবে না: "
    "<b>, <i>, <u>, <s>, <code>, <blockquote>, <tg-spoiler>, <a>। "
    "নিষিদ্ধ: '#', '**', বা decorative dash '_'। "
    "পোস্টের দৈর্ঘ্য ৭০০-৯০০ অক্ষরের মধ্যে রাখো।"
)


# ---------------------------------------------------------------------------
# Text AI
# ---------------------------------------------------------------------------


async def _google_ai(
    prompt: str, system: str, model: str, api_key: str
) -> str:
    if not api_key:
        raise RuntimeError("Google AI key অনুপস্থিত")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system}]},
        "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1024},
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:  # pragma: no cover
        raise RuntimeError(f"Google AI response parse error: {e!r} -> {data}")


async def _openai_compatible(
    prompt: str,
    system: str,
    model: str,
    api_key: str,
    base_url: str,
) -> str:
    if not api_key:
        raise RuntimeError("API key অনুপস্থিত")
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 1024,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"]


async def generate_text(
    prompt: str,
    *,
    settings,
    db,
    role_override: str | None = None,
    provider_override: str | None = None,
    model_override: str | None = None,
) -> str:
    """প্রম্পট থেকে বাংলা কনটেন্ট তৈরি করে।"""
    role = role_override or db.get_setting(
        "ai_role", "একজন অভিজ্ঞ বাংলা কনটেন্ট রাইটার"
    )
    system = f"{role}\n\n{SYSTEM_RULES}"
    provider = (provider_override or db.get_setting("text_ai_provider", "google")).lower()
    model = model_override or db.get_setting("text_ai_model", "")

    if provider == "google":
        text = await _google_ai(
            prompt,
            system,
            model or "gemini-2.5-flash",
            settings.google_ai_key,
        )
    elif provider == "openrouter":
        text = await _openai_compatible(
            prompt,
            system,
            model or "meta-llama/llama-3.3-8b-instruct:free",
            settings.openrouter_key,
            "https://openrouter.ai/api/v1",
        )
    elif provider == "custom":
        text = await _openai_compatible(
            prompt,
            system,
            model or settings.custom_ai_model or "gpt-3.5-turbo",
            settings.custom_ai_key,
            settings.custom_ai_url or "https://api.openai.com/v1",
        )
    else:
        raise RuntimeError(f"অজানা টেক্সট AI প্রোভাইডার: {provider}")

    return sanitize_html(text.strip())


# ---------------------------------------------------------------------------
# Image AI
# ---------------------------------------------------------------------------


async def _ghostweb_image(prompt: str, api_key: str, model: str) -> bytes:
    """infip.pro / GhostWeb-style endpoint।"""
    if not api_key:
        raise RuntimeError("GhostWeb key অনুপস্থিত")
    url = "https://api.infip.pro/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model or "img4", "prompt": prompt, "n": 1, "size": "1024x1024"}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        image_url = (
            data.get("data", [{}])[0].get("url")
            or data.get("output", [None])[0]
        )
        if not image_url:
            raise RuntimeError("GhostWeb returned no image URL")
        ir = await client.get(image_url)
        ir.raise_for_status()
        return ir.content


async def _pollinations_image(prompt: str) -> bytes:
    encoded = urllib.parse.quote(prompt[:300])
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content


async def generate_image(
    prompt: str, *, settings, db, provider_override: str | None = None
) -> bytes | None:
    provider = (
        provider_override or db.get_setting("image_ai_provider", "pollinations")
    ).lower()
    if provider == "none":
        return None
    try:
        if provider == "ghostweb":
            model = db.get_setting("image_ai_model", "img4")
            return await _ghostweb_image(prompt, settings.ghostweb_key, model)
        if provider == "pollinations":
            return await _pollinations_image(prompt)
    except Exception as e:  # noqa: BLE001
        log.warning("Image generation failed (%s): %s", provider, e)
        # fallback to pollinations
        if provider != "pollinations":
            try:
                return await _pollinations_image(prompt)
            except Exception as e2:  # noqa: BLE001
                log.warning("Pollinations fallback also failed: %s", e2)
    return None


async def chat_test(prompt: str, *, settings, db) -> str:
    """অ্যাডমিন প্যানেল থেকে সরাসরি AI চ্যাট পরীক্ষা।"""
    try:
        return await generate_text(prompt, settings=settings, db=db)
    except Exception as e:  # noqa: BLE001
        return f"⚠️ ত্রুটি: {e}"
