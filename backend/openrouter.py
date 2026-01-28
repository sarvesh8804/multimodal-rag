import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
import io

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

VISION_MODEL = "google/gemma-3-12b-it:free"


def encode_image(path):
    img = Image.open(path).convert("RGB")
    img.thumbnail((1024, 1024))   # resize for vision model

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    return base64.b64encode(buf.getvalue()).decode()


def ask_vision(image_path: str, user_query: str):
    image_b64 = encode_image(image_path)

    prompt = f"""
Look at this image and answer the question using the information visible in it.

Question: {user_query}

Answer briefly.
"""

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ],
            }
        ],
        max_tokens=400,
        extra_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "vision-test"
        }
    )

    # ---- DEBUG ----
    print("RAW RESPONSE:", response)

    if not response or not hasattr(response, "choices") or not response.choices:
        raise RuntimeError("OpenRouter returned no choices. Model likely blocked for your account.")

    return response.choices[0].message.content.strip()



if __name__ == "__main__":
    image_path = "image.png"   # <-- path to your PDF page image
    query = "what is the revenue in 1997 ?"

    answer = ask_vision(image_path, query)

    print("Query:", query)
    print("Answer:", answer)
