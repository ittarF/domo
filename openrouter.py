# === openrouter.py ===
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def get_openrouter_response(messages, model: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENROUTER_API_KEY in .env")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "OpenRouter Client"
    }

    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"OpenRouter API error: {resp.status}")
            result = await resp.json()
            print(result)
            return result["choices"][0]["message"]["content"].strip()
