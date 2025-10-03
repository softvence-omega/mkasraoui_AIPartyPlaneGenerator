# import google.generativeai as genai
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
# from google.api_core.exceptions import ServiceUnavailable
# import json

# from app.config import PRODUCT_MODEL, GEMINI_API_KEY, PARTY_PLANNER_PROMPT, PRODUCT_PROMPT
# from app.utils.logger import get_logger
# from app.schemas.schema import PartyInput
# from app.services.party.adventure_list import search_youtube_videos

# logger = get_logger(__name__)



# class PartyPlanGenerator:


#     @staticmethod
#     def model_client():
#         try:
#             genai.configure(api_key=GEMINI_API_KEY)
#             config = genai.GenerationConfig(
#                 response_mime_type="application/json"
#             )
#             return genai, config

#         except Exception as e:
#             logger.error(f"Error in model client: {e}")
#             raise e


#     @retry(
#         stop = stop_after_attempt(3),
#         wait = wait_exponential(multiplier = 1, min = 4, max = 10),
#         retry = retry_if_exception_type(ServiceUnavailable)
#     )
#     def _make_api_call(self, client, model, contents, config):
#         model_instance = client.GenerativeModel(model)
#         return model_instance.generate_content(
#             contents=contents,
#             generation_config=config
#         )


#     def generate_party_plan(self, party_input : PartyInput):

#         try:
#             party_prompt = [
#                 {
#                     "parts" : [
#                         {"text": PARTY_PLANNER_PROMPT.format(
#                             person_name=party_input.person_name,
#                             person_age=party_input.person_age,
#                             theme=party_input.party_details.theme,
#                             favorite_activities=party_input.party_details.favorite_activities,
#                             num_guests=party_input.num_guests,
#                             budget=party_input.budget,
#                             party_date=party_input.party_date,
#                             location=party_input.location)}
#                     ]
#                 }
#             ]

#             ## Model
#             logger.info("Generating party plan...")
#             client , config = self.model_client()
#             response = self._make_api_call(client, PRODUCT_MODEL, party_prompt, config)
#             raw_text = response.text.strip()
#             json_data = json.loads(raw_text)
#             suggest_gift = json_data.get("🎁 Suggested Gifts")

#             return json_data, suggest_gift
#         except Exception as e:
#             logger.error(f"Error in generate party plan: {e}")
#             raise e


#     def suggested_gifts(self, product, suggest_gifts, how_many):
#         try:
#             gifts_prompt = [
#                 {
#                     "parts" : [
#                         {"text": PRODUCT_PROMPT.format(
#                             product_json=product,
#                             suggested_gifts=suggest_gifts,
#                             top_n=how_many)}
#                     ]
#                 }
#             ]

#             logger.info("Generating Gift list...")
#             client , config = self.model_client()
#             response = self._make_api_call(client, PRODUCT_MODEL, gifts_prompt, config)
#             raw_text = response.text.strip()
#             json_data = json.loads(raw_text)
#             return json_data

#         except Exception as e:
#             logger.error(f"Error in suggest gifts: {e}")
#             raise e

#     def generate_youtube_links(self, theme: str, age: int) -> List[dict]:
#         try:
#             query = f"fun party music for age {age} with theme {theme}"
#             videos = search_youtube_videos(query, max_results=5)
#             return videos
#         except Exception as e:
#             logger.error(f"Error in generate youtube links: {e}")
#             return []
        
        
        
# if __name__ == "__main__":
    
#     party_input = PartyInput(
#         person_name="Alice",
#         person_age=10,
#         budget=500,
#         num_guests=15,
#         party_date="2023-12-15",
#         location="Wonderland",
#         party_details={
#             "theme": "Superhero",
#             "favorite_activities": ["Treasure Hunt", "Magic Show"]
#         }
#     )

#     party_plan_generator = PartyPlanGenerator()
#     party_plan, gift_list = party_plan_generator.generate_party_plan(party_input)
#     print("Party Plan:", json.dumps(party_plan, indent=2))
#     print("Suggested Gifts:", json.dumps(gift_list, indent=2))

#     # Example of generating YouTube links
#     youtube_links = party_plan_generator.generate_youtube_links(party_input.party_details.theme, party_input.person_age)
#     print("YouTube Links:", json.dumps(youtube_links, indent=2))



import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ServiceUnavailable
import json
from typing import List, Dict, Any

from app.config import PRODUCT_MODEL, GEMINI_API_KEY, PARTY_PLANNER_PROMPT, PRODUCT_PROMPT
from app.utils.logger import get_logger
from app.schemas.schema import PartyInput
from app.services.party.adventure_list import search_youtube_videos
from app.utils.helper import filter_data

logger = get_logger(__name__)


class PartyPlanGenerator:
    @staticmethod
    def model_client():
        """Configure Gemini AI client."""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            config = genai.GenerationConfig(response_mime_type="application/json")
            return genai, config
        except Exception as e:
            logger.error(f"Error in model client: {e}")
            raise e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(ServiceUnavailable),
    )
    def _make_api_call(self, client, model, contents, config):
        """Call Gemini AI with retries."""
        model_instance = client.GenerativeModel(model)
        return model_instance.generate_content(
            contents=contents,
            generation_config=config
        )

    def generate_party_plan(self, party_input: PartyInput):
        """Generate party plan JSON using AI."""
        try:
            party_prompt = [
                {
                    "parts": [
                        {"text": PARTY_PLANNER_PROMPT.format(
                            person_name=party_input.person_name,
                            person_age=party_input.person_age,
                            theme=party_input.party_details.theme,   # ✅ fixed
                            favorite_activities=party_input.party_details.favorite_activities,  # ✅ fixed
                            num_guests=party_input.num_guests,
                            budget=party_input.budget,
                            party_date=party_input.party_date,
                            location=party_input.location
                        )}
                    ]
                }
            ]

            logger.info("Generating party plan...")
            client, config = self.model_client()
            response = self._make_api_call(client, PRODUCT_MODEL, party_prompt, config)
            raw_text = response.text.strip()
            party_json = json.loads(raw_text)

            # Extract suggested gifts
            suggested_gifts = party_json.get("🎁 Suggested Gifts", [])
            return party_json, suggested_gifts

        except Exception as e:
            logger.error(f"Error in generate_party_plan: {e}")
            raise e


    def suggested_gifts(self, product_list: List[str], suggested_gifts: List[str], top_n: int):
        """Generate detailed gift info JSON using AI."""
        try:
            gifts_prompt = [
                {
                    "parts": [
                        {"text": PRODUCT_PROMPT.format(
                            product_json=product_list,
                            suggested_gifts=suggested_gifts,
                            top_n=top_n
                        )}
                    ]
                }
            ]

            logger.info("Generating detailed gift list...")
            client, config = self.model_client()
            response = self._make_api_call(client, PRODUCT_MODEL, gifts_prompt, config)
            raw_text = response.text.strip()
            gifts_json = json.loads(raw_text)
            return gifts_json

        except Exception as e:
            logger.error(f"Error in suggested_gifts: {e}")
            return []
        
        

    def generate_youtube_links(self, theme: str, age: int) -> List[dict]:
        """Fetch YouTube music/movie links for the party."""
        try:
            query = f"fun party music/movie for age {age} with theme {theme}"
            videos = search_youtube_videos(query, max_results=5)
            return videos
        except Exception as e:
            logger.error(f"Error in generate_youtube_links: {e}")
            return []

    def generate_full_party_json(self, party_input: PartyInput, product: dict) -> Dict[str, Any]:
        """Generate final structured party JSON for frontend."""
        try:
            # 1️⃣ AI Party Plan
            party_json, suggested_gifts_list = self.generate_party_plan(party_input)
            
           
            logger.info(f"Party Plan JSON: {party_json}")
            
            new_party_ideas = {
                "🎨 Theme & Decorations": party_json.get("🎨 Theme & Decorations", []),
                "🎉 Fun Activities": party_json.get("🎉 Fun Activities", []),
                "🍔 Food & Treats": party_json.get("🍔 Food & Treats", []),
                "🛍️ Party Supplies": party_json.get("🛍️ Party Supplies", []),
                "⏰ Party Timeline": party_json.get("⏰ Party Timeline", [])
            }
            logger.info(f"Suggested Gifts List: {suggested_gifts_list}")
            # 2️⃣ YouTube links
            music_links = self.generate_youtube_links(
                theme=party_input.party_details.theme,   # ✅ fixed
                age=party_input.person_age
            )

            # 3️⃣ Detailed Gift Suggestions
            gifts_json = self.suggested_gifts(
                product_list=party_json.get("🎁 Suggested Gifts", []),
                suggested_gifts=suggested_gifts_list,
                top_n=len(suggested_gifts_list),
            )
            logger.info(f"Detailed Gifts JSON: {gifts_json}")

            filtered_data = filter_data(product["data"], party_input.budget)
            
            return {
                "party_plan": new_party_ideas,
                "suggested_gifts": filtered_data,
                "adventure_song_movie_links": music_links
            }

        except Exception as e:
            logger.error(f"Error generating full party JSON: {e}")
            raise e



if __name__ == "__main__":
    # Example run
    party_input = PartyInput(
        person_name="Alice",
        person_age=10,
        budget=500,
        num_guests=15,
        party_date="2023-12-15",
        location="Wonderland",
        party_details={
            "theme": "Superhero",
            "favorite_activities": ["Treasure Hunt", "Magic Show"]
        }
    )

    party_plan_generator = PartyPlanGenerator()
    full_party_json = party_plan_generator.generate_full_party_json(party_input, product)
    print("Full Party JSON:", json.dumps(full_party_json, indent=2))
