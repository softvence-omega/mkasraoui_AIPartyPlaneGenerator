import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ServiceUnavailable
import json

from app.config import PRODUCT_MODEL, GEMINI_API_KEY, PARTY_PLANNER_PROMPT, PRODUCT_PROMPT
from app.utils.logger import get_logger
from app.schemas.schema import PartyInput


logger = get_logger(__name__)



class PartyPlanGenerator:


    @staticmethod
    def model_client():
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            config = genai.GenerationConfig(
                response_mime_type="application/json"
            )
            return genai, config

        except Exception as e:
            logger.error(f"Error in model client: {e}")
            raise e


    @retry(
        stop = stop_after_attempt(3),
        wait = wait_exponential(multiplier = 1, min = 4, max = 10),
        retry = retry_if_exception_type(ServiceUnavailable)
    )
    def _make_api_call(self, client, model, contents, config):
        model_instance = client.GenerativeModel(model)
        return model_instance.generate_content(
            contents=contents,
            generation_config=config
        )


    def generate_party_plan(self, party_input : PartyInput):

        try:
            party_prompt = [
                {
                    "parts" : [
                        {"text": PARTY_PLANNER_PROMPT.format(
                            person_name=party_input.person_name,
                            person_age=party_input.person_age,
                            theme=party_input.party_details.theme,
                            favorite_activities=party_input.party_details.favorite_activities,
                            num_guests=party_input.num_guests,
                            budget=party_input.budget,
                            party_date=party_input.party_date,
                            location=party_input.location)}
                    ]
                }
            ]

            ## Model
            logger.info("Generating party plan...")
            client , config = self.model_client()
            response = self._make_api_call(client, PRODUCT_MODEL, party_prompt, config)
            raw_text = response.text.strip()
            json_data = json.loads(raw_text)
            suggest_gift = json_data.get("🎁 Suggested Gifts")

            return json_data, suggest_gift
        except Exception as e:
            logger.error(f"Error in generate party plan: {e}")
            raise e


    def suggested_gifts(self, product, suggest_gifts, how_many):
        try:
            gifts_prompt = [
                {
                    "parts" : [
                        {"text": PRODUCT_PROMPT.format(
                            product_json=product,
                            suggested_gifts=suggest_gifts,
                            top_n=how_many)}
                    ]
                }
            ]

            logger.info("Generating Gift list...")
            client , config = self.model_client()
            response = self._make_api_call(client, PRODUCT_MODEL, gifts_prompt, config)
            raw_text = response.text.strip()
            json_data = json.loads(raw_text)
            return json_data

        except Exception as e:
            logger.error(f"Error in suggest gifts: {e}")
            raise e
