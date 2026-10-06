"""
Automated Copywriting & Tone Transformer - Google Gemini Version
------------------------------------------------------------
Ye script product ki info leti hai aur alag-alag platforms (LinkedIn,
Instagram, Facebook, WhatsApp, Email) ke liye marketing copy generate
karti hai, user ki di hui "tone" ke hisaab se. Ye Google Gemini API
use karti hai (free tier available).

Kaise chalayein (Terminal mein):
    python copywriter_gemini.py --product "Wireless Earbuds" --description "Noise cancelling, 20hr battery" --platform instagram --tone witty

Setup:
    1. pip install google-genai
    2. Free API key lo: https://aistudio.google.com/app/apikey
    3. Is script wali folder mein ek ".env" naam ki file banao aur usme likho:
       GEMINI_API_KEY=your_key_here
       (Ab har baar terminal mein key set karne ki zaroorat nahi, ye file se khud aa jayegi)
"""

import argparse
import os
import time
from google import genai
from google.genai import types
from google.genai import errors


def load_env_file(filepath=".env"):
    """.env file ko khud se parse karta hai (koi extra library nahi chahiye)."""
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env_file()  # .env file se GEMINI_API_KEY khud load ho jayegi

# Har platform ke apne rules hain - character limit, style, hashtags waghera
PLATFORM_RULES = {
    "linkedin": "Professional tone. Max 3000 characters. End with 1-2 relevant hashtags.",
    "instagram": "Catchy and visual. Max 2200 characters. Use 3-5 hashtags and some emojis.",
    "facebook": "Friendly and conversational. Max 500 characters. Encourage likes/comments/shares.",
    "whatsapp": "Short and personal, like a message to a friend. Max 300 characters. No hashtags.",
    "email": "Formal structure with Subject line, Greeting, Body, and a clear Call-to-Action. Max 500 words.",
}


def build_prompt(product_name, platform, tone, description):
    """User ki values ko ek 'master template' mein fit karta hai (f-string se)."""
    platform_key = platform.lower()
    rules = PLATFORM_RULES.get(platform_key, "Write general marketing copy.")

    prompt = f"""
You are a professional marketing copywriter.

Product Name: {product_name}
Product Description: {description}
Target Platform: {platform}
Tone: {tone}

Platform Rules: {rules}

Write marketing copy for this product following the platform rules and tone above.
"""
    return prompt.strip()


def generate_copy(prompt, temperature, top_p):
    """Gemini model ko call karta hai aur generated text wapis deta hai."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable set nahi hai. "
            "PowerShell mein set karo: $env:GEMINI_API_KEY=\"apni_key\""
        )

    client = genai.Client(api_key=api_key)

    max_attempts = 6
    wait_seconds = 5

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=top_p,
                ),
            )
            return response.text
        except errors.ServerError:
            if attempt == max_attempts:
                raise
            print(f"Model busy hai (attempt {attempt}/{max_attempts}). {wait_seconds} seconds ruk kar dobara try kar raha hoon...")
            time.sleep(wait_seconds)
            wait_seconds *= 2  # har baar zyada wait karo (exponential backoff)


def main():
    parser = argparse.ArgumentParser(description="Automated Copywriting & Tone Transformer (Gemini)")
    parser.add_argument("--product", required=True, help="Product ka naam")
    parser.add_argument("--description", required=True, help="Product ki short description")
    parser.add_argument(
        "--platform",
        required=True,
        choices=list(PLATFORM_RULES.keys()),
        help="Target platform: linkedin, instagram, facebook, whatsapp, email",
    )
    parser.add_argument("--tone", required=True, help="Tone, jaise: witty, professional, casual, persuasive")
    parser.add_argument("--temperature", type=float, default=0.7, help="Creativity level (0.0 se 1.0 tak)")
    parser.add_argument("--top_p", type=float, default=1.0, help="Nucleus sampling value")
    args = parser.parse_args()

    prompt = build_prompt(args.product, args.platform, args.tone, args.description)
    print("\n--- Generated Prompt (jo AI ko bheja gaya) ---")
    print(prompt)

    copy_text = generate_copy(prompt, args.temperature, args.top_p)
    print("\n--- Final Marketing Copy ---")
    print(copy_text)


if __name__ == "__main__":
    main()