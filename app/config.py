import os
from dotenv import load_dotenv
from pathlib import Path

# load .env
load_dotenv(override=True)

## API KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

## cloudinary api key
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

## Constant
LOG_DIR = "logs"
TEMP_FOLDER_NAME = "temp"
MODEL_NAME = "gemini-2.5-flash-image-preview"
TEMPERATURE = 2.0
GENERATED_IMG_PATH = Path("data")

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

    Dynamic Parameters:
    - T-shirt type: {tshirt_type} (e.g., child, adult)
    - Gender: {gender}
    - Age: {age}
    - Theme: {theme} (e.g., pirate, princess, superhero, fantasy, sports)
    - Optional message: {message} (e.g., "Happy Birthday Nick!", "Adventure Awaits", etc.)

    Birthday-Specific Requirements:
    - The artwork must clearly feel like it belongs to a **birthday celebration**.
    - Include festive elements: confetti, balloons, streamers, cake, or theme-consistent accents.
    - Composition must be colorful, bold, and joyful.
    - Design should be crisp, flat, vector-like, with no background clutter, ensuring it prints cleanly on fabric.
    """


SHIRT_MOCKUP_PROMPT = """
    Create a realistic, professional t-shirt mockup for showcasing how the uploaded artwork will look when printed.

    Requirements:
    - Use the **uploaded image** as the design to be printed on the t-shirt (do not recreate or modify the artwork).
    - T-shirt color: {tshirt_color}
    - T-shirt size: {tshirt_size}
    - Intended age group: {age} (e.g., child, teen, adult)

    Mockup Specifications:
    - The uploaded artwork must appear **naturally printed** on the t-shirt fabric (not floating or pasted).
    - Show realistic fabric folds, shadows, and highlights to emphasize the print placement.
    - Ensure the uploaded artwork scales properly to the t-shirt size without distortion.
    - Use a plain, minimal background to keep focus on the t-shirt itself.
    - Present the mockup in a clean, professional product-photo style, suitable for an online store showcase.

    ⚠️ Only generate the mockup of the t-shirt with the uploaded image printed — do not include duplicate designs, separate posters, or additional product variations.
    """


