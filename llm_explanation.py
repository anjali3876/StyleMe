import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


def generate_outfit_explanation(
    top,
    bottom,
    shoes,
    style,
    occasion,
    weather_type,
    temperature
):
    if not HF_TOKEN:
        return (
            "This outfit was selected based on your style, "
            "occasion, wardrobe colours and today's weather."
        )

    client = InferenceClient(
        api_key=HF_TOKEN,
        provider="auto"
    )

    prompt = f"""
You are StyleMe, a friendly AI fashion assistant.

Explain why this outfit works.

Style: {style}
Occasion: {occasion}
Weather: {weather_type}
Temperature: {temperature}°C

Top: {top.name}, colour {top.colour}
Bottom: {bottom.name}, colour {bottom.colour}
Shoes: {shoes.name}, colour {shoes.colour}

Give a short, natural explanation in 2-3 sentences.
Mention the style, weather and colour coordination.
Do not invent clothing items that are not listed.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise and friendly fashion "
                        "assistant for a wardrobe recommendation app."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=120,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return (
            "This outfit was selected to match your style, "
            "occasion and today's weather. 💗"
        )