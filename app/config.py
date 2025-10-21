# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary
from google import genai



# Load env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Initialize Google GenAI client (Gemini)
GENAI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# local directory for generated images
BASE_DIR = os.getcwd()
GENERATED_DIR = os.path.join(BASE_DIR, "generated_cards")
os.makedirs(GENERATED_DIR, exist_ok=True)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
## cloudinary api key
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

## Constant
LOG_DIR = "logs"
TEMP_FOLDER_NAME = "temp"
MODEL_NAME = "gemini-2.5-flash-image-preview"
PRODUCT_MODEL = "gemini-2.5-flash"
TEMPERATURE = 1.0
GENERATED_IMG_PATH = Path("data")
PRODUCT_API = "https://api.mafetefacile.fr/affiliate-product"

# Prompt
IMAGE_ANALYSIS_PROMPT = """
    If an image is uploaded:
    - First, analyze the uploaded image and generate a highly detailed, structured, and comprehensive description.
    - The description must be organized into the following categories and optimized for use as a prompt for a high-quality image generator:

    **Overall Composition:** Describe the main subject, its arrangement within the frame, and the general layout. Mention elements like symmetry, asymmetry, depth, and perspective.

    **Dominant Colors:** List the most prominent colors in the image and their general tone (e.g., vibrant, muted, pastel, dark).

    **Shapes:** Identify the primary shapes present in the image, both in the main subject and the background (e.g., geometric, organic, curvilinear, angular).

    **Texture and Material:** Describe any visible textures or implied materials (e.g., smooth, rough, metallic, fabric, wood, glossy).

    **Lighting:** Characterize the lighting conditions (e.g., bright, dim, soft, harsh, natural, artificial, time of day, direction of light, presence of shadows or highlights).

    **Style:** Define the artistic or photographic style of the image (e.g., realistic, abstract, impressionistic, minimalist, retro, futuristic, photorealistic, painterly, cartoon, vector art).

    **Details:** Provide specific observations about intricate elements, patterns, specific objects, or unique features that contribute to the image's character.

    **Mood/Atmosphere:** Describe the overall feeling or emotion evoked by the image (e.g., calm, energetic, mysterious, joyful, somber, professional, whimsical).

    **Keywords:** Generate a list of relevant keywords that succinctly describe the image's content, style, and potential themes, suitable for image search or tagging.

    ---
    After the analysis:
    - Use the uploaded image as the **primary creative reference** for the final design, ensuring its style, subject traits, and inspiration are carried into the generated birthday artwork.

    If NO image is uploaded:
    - Skip the analysis step.
    - Instead, generate the artwork entirely based on the dynamic parameters provided below.

    ⚠️ STRICT REQUIREMENTS FOR FINAL OUTPUT:
    - Do NOT generate a t-shirt, mockup, or product photo.
    - The output must be a **standalone design/artwork only**, ready for printing.
    - Artwork must have a **transparent background**.
    - The design should be centered, isolated, and optimized for **fabric printing**.
    - **Never invent random placeholder names (e.g., Nick, John, Mary).**
    - If `{message}` is provided, interpret its meaning and integrate it into the artwork appropriately:
    - If it is a greeting (e.g., “Happy Birthday Sarah!”), render it as festive text in the design.
    - If it is descriptive (e.g., “I want red balloons” / “Make it adventurous with mountains”), integrate those visual elements into the artwork instead of just adding the words.
    - If `{message}` is not provided, infer a short, festive, context-appropriate birthday greeting or decoration idea from the uploaded image, theme, age, or celebration style.

    Dynamic Parameters:
    - T-shirt type: {tshirt_type} (e.g., child, adult)
    - Gender: {gender}
    - Age: {age}
    - Theme: {theme} (e.g., pirate, princess, superhero, fantasy, sports)
    - Optional message: {message}

    Birthday-Specific Requirements:
    - The artwork must clearly feel like it belongs to a **birthday celebration**.
    - Include festive elements: confetti, balloons, streamers, cake, or theme-consistent accents.
    - Composition must be colorful, bold, and joyful.
    - Design should be crisp, flat, vector-like, with no background clutter, ensuring it prints cleanly on fabric.
    """


SHIRT_MOCKUP_PROMPT = SHIRT_MOCKUP_PROMPT = """
    Create a realistic, professional product mockup showcasing how the uploaded artwork will appear when printed on the selected apparel.

    Requirements:
    - Apparel type: {apparel_type} (e.g., T-shirt, Sweatshirt, Hoodie, Tank Top)
    - Apparel color: {tshirt_color}
    - Apparel size: {tshirt_size}
    - Intended age group: {age} (e.g., child, teen, adult)
    - Gender: {gender} (e.g., male, female, unisex)
    - Use the **uploaded image** as the design to be printed on the apparel (do not recreate, modify, or reposition the artwork).

    Mockup Specifications:
    - The uploaded artwork must appear **naturally printed** on the fabric of the specified apparel type (not floating or pasted).
    - Do **not** include any human models, mannequins, hangers, or background props — show only the apparel item itself.
    - Display the apparel laid flat or presented as a standalone 3D product view.
    - Include realistic fabric texture, folds, lighting, and shadows to emphasize natural print placement.
    - Ensure the design scales properly to the apparel size, gender, and type without distortion.
    - Use a **plain white background** (no gradients or scenery) to keep full focus on the apparel.
    - Present the mockup in a clean, professional, store-ready product photo style.

    ⚠️ Only generate the mockup of the specified apparel with the uploaded image printed on it — do not include duplicate designs, extra variations, or unrelated products.
    """



PARTY_PLANNER_PROMPT = """
        You are an AI party planner. Generate a birthday party plan based on:
        Name: {person_name}, Age: {person_age}, Budget: ${budget},
        Guests: {num_guests}, Date: {party_date}, Location: {location},
        Theme: {theme}, Favorite Activities: {favorite_activities}
    
        Return JSON with emojis like below, and include these gift suggestions in "🎁 Suggested Gifts":
    
        {{
        "🎨 Theme & Decorations": ["bullet point instructions"],
        "🎉 Fun Activities": ["list of activities"],
        "🍔 Food & Treats": ["list of food items"],
        "🛍️ Party Supplies": ["list of supplies"],
        "⏰ Party Timeline": ["timeline steps with emojis"],
        "🎁 Suggested Gifts": ["list of gift names only"],
        "🌟 New Adventure Ideas": ["list of adventure/fun ideas"],
        }}
    """

PRODUCT_PROMPT = """
You are an assistant that selects products from a given product JSON based on a suggested gifts list.

### Instructions:
1. Carefully read the provided `product_json`.
2. Read the `suggested_gifts` list.
3. Compare each product against the `suggested_gifts` and **rank them by relevance/similarity**.
   - Consider title, price, average rating, total reviews, or any other relevant attributes.
4. Return ONLY the top {top_n} most relevant products with their `id`, `title`, `link`, `price`, `avg_rating`, `total_review`, `image_url`, and `affiliated_company`.
5. If fewer than {top_n} products match, return only the available ones.
6. Output must be in **valid JSON format** with this structure:
{{
  "products": [
    {{
      "id": "id1",
      "title": "title1",
      "link": "link1",
      "price": 0.0,
      "avg_rating": 0,
      "total_review": 0,
      "image_url": "image_url1",
      "affiliated_company": "company1"
    }},
    {{
      "id": "id2",
      "title": "title2",
      "link": "link2",
      "price": 0.0,
      "avg_rating": 0,
      "total_review": 0,
      "image_url": "image_url2",
      "affiliated_company": "company2"
    }}
    ... up to {top_n}
  ]
}}

⚠️ Rules:
- Do not return any extra explanation or text.
- If no product matches, return:
{{
  "products": []
}}

---

### product_json:
{product_json}

### suggested_gifts:
{suggested_gifts}
"""
