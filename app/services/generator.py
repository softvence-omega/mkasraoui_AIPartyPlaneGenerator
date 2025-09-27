# app/services/generator.py
import os
import time
import uuid
from io import BytesIO
from PIL import Image
from typing import Dict, List

from google.genai import types
from google.genai.errors import ClientError

import cloudinary.uploader

from app.config import GENAI_CLIENT, GENERATED_DIR

# Build the same image prompt generator as in your notebook
def build_image_prompt(data: Dict) -> str:
    prompt = f"A {data.get('theme', 'modern')} style birthday invitation card.\n"
    if data.get("description"):
        prompt += f"Theme description: {data['description']}\n"
    if data.get("age"):
        prompt += f"Age: {data['age']}\n"
    if data.get("birthday_person_name"):
        prompt += f"Main text: 'Join us for {data['birthday_person_name']}'s Birthday!'\n"
    if data.get("venue") or data.get("date") or data.get("time") or data.get("contact_info"):
        details = []
        if data.get("venue"):
            details.append(f"Venue: {data['venue']}")
        if data.get("date"):
            details.append(f"Date: {data['date']}")
        if data.get("time"):
            details.append(f"Time: {data['time']}")
        if data.get("contact_info"):
            details.append(f"RSVP: {data['contact_info']}")
        prompt += "Details: " + ", ".join(details) + "\n"
    if data.get("custom_message"):
        prompt += f"Custom message: {data['custom_message']}\n"
    else:
        prompt += "Use generic decorative graphics/icons instead of a personal photo.\n"

    system_prompt = f"""
You are an expert birthday invitation card designer AI. Generate a visually appealing, age-appropriate, and theme-consistent design description.

Guidelines:
- Include the birthday person's name, age, and gender if provided.
- Match the design with the specified theme.
- Use colors, fonts, and graphics that are age-appropriate:
    * Kids → bright, fun, cartoonish
    * Teens → stylish, trendy
    * Adults → elegant, modern
    * Seniors → classic, warm
- Gender-specific styling:
    * Boy → superhero/cool tones
    * Girl → princess/floral tones
    * Other/neutral → vibrant, inclusive
- Rich text styling:
    * Bold for important details (name, date, venue)
    * Italics for greetings, taglines, quotes
    * Highlight the age
- Must include:
    * Creative greeting line
    * Birthday person’s name prominently
    * Venue, date, time clearly shown if provided
    * RSVP/contact info at the bottom if provided
    * Custom message prominently displayed if provided
- Make it colorful, attractive, and celebratory.

Card content to use as a starting point:
{prompt}
Generate a detailed design description for the card image based on these inputs.
"""
    return system_prompt

def generate_invitation_text(data: Dict) -> str:
    prompt_text = f"""
Create a short and fun birthday invitation message in 10-15 words.
Theme: {data.get('theme')}
Person: {data.get('birthday_person_name')}, Age: {data.get('age')}
"""
    resp = GENAI_CLIENT.models.generate_content(
        model="gemini-2.5-pro",
        contents=[types.Part(text=prompt_text)]
    )
    invitation_text = ""
    if resp.candidates:
        candidate = resp.candidates[0]
        if candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    invitation_text += part.text.strip() + " "
    return invitation_text.strip()

def generate_birthday_card_image(data: Dict, output_prefix: str = "birthday_card") -> List[Dict]:
    prompt = build_image_prompt(data)
    response = GENAI_CLIENT.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[types.Part(text=prompt)]
    )

    uploaded = []
    # Candidate might have inline_data parts with raw bytes
    candidate = response.candidates[0]
    for i, part in enumerate(candidate.content.parts):
        inline = getattr(part, "inline_data", None)
        if inline and getattr(inline, "data", None):
            raw = inline.data  # bytes
            image = Image.open(BytesIO(raw))
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            fname = f"{output_prefix}_{int(time.time())}_{uuid.uuid4().hex[:8]}.png"
            local_path = os.path.join(GENERATED_DIR, fname)
            image.save(local_path)

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(local_path, folder="birthday_cards")
            uploaded.append({
                "url": upload_result.get("secure_url"),
                "public_id": upload_result.get("public_id")
            })
    return uploaded
