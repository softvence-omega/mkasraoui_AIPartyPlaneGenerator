from google import genai
from google.genai.types import GenerateContentConfig, Modality


from app.utils.logger import get_logger
from app.utils.helper import upload_image
from app.config import IMAGE_ANALYSIS_PROMPT, GEMINI_API_KEY, MODEL_NAME, TEMPERATURE, SHIRT_MOCKUP_PROMPT




logger = get_logger(__name__)


# 1. t-shirt Design
# 2. t-shirt mockup

class TShirt:

    def __init__(self,tshirt_type, tshirt_size, gender, age, theme, color, message = None):
        self.tshirt_type = tshirt_type
        self.tshirt_size = tshirt_size
        self.gender = gender
        self.age = age
        self.theme = theme
        self.color = color
        self.message = message


    ## model
    @staticmethod
    def model_client():
        try:
            logger.info("Initializing model client...")

            client = genai.Client(api_key=GEMINI_API_KEY)

            config = GenerateContentConfig(
                response_modalities=[Modality.TEXT, Modality.IMAGE],
                temperature=TEMPERATURE
            )

            return client, config
        except Exception as e:
            logger.error(f"Error in model client: {e}")
            raise e


    ## T-Shirt Design
    def generate_shirt_design(self, ref_img_path):
        try:
            t_shirt_content = [
                {
                    "parts": [
                        {"inline_data": upload_image(ref_img_path)},
                        {"text": IMAGE_ANALYSIS_PROMPT.format(tshirt_type=self.tshirt_type, gender=self.gender, age=self.age, theme=self.theme, message=self.message, color=self.color)}
                    ]
                }
            ]

            ## Model
            logger.info("Generating t-shirt design...")
            client, config = self.model_client()

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=t_shirt_content,
                config=config
            )
            logger.info("T-shirt design generated successfully.")
            return response
        except Exception as e:
            logger.error(f"Error in shirt design: {e}")
            raise e

    # T-Shirt Mockup Design
    def generate_shirt_mockup(self, generated_design):
        try:
            t_shirt_mockup_content = [
                {
                    "parts": [
                        {"inline_data": upload_image(generated_design)},
                        {"text": SHIRT_MOCKUP_PROMPT.format(tshirt_color=self.color, tshirt_size=self.tshirt_size, age=self.age)}
                    ]
                }
            ]

            ## Model
            logger.info("Generating t-shirt mockup...")
            client, config = self.model_client()

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=t_shirt_mockup_content,
                config=config
            )
            logger.info("T-shirt mockup generated successfully.")
            return response
        except Exception as e:
            logger.error(f"Error in shirt mockup: {e}")
            raise e

