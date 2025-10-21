import google.generativeai as genai
from sympy import product
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ServiceUnavailable
import json
from typing import List, Dict, Any, Union
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
            print("gift_prompt--------------------",gifts_prompt)
            logger.info("Generating detailed gift list...")
            client, config = self.model_client()
            print("prompt--------------------",gifts_prompt)
            response = self._make_api_call(client, PRODUCT_MODEL, gifts_prompt, config)
            
            
            print("api response--------------------------",response)
            raw_text = response.text.strip()
            gifts_json = json.loads(raw_text)
            return gifts_json

        except Exception as e:
            logger.error(f"Error in suggested_gifts: {e}")
            return []
        
        

    def generate_youtube_links(self, theme: str, age: int) -> List[dict]:
        """Fetch YouTube music/movie links for the party."""
        try:
            query = f"fun party music/song for age {age} with theme {theme}"
            videos = search_youtube_videos(query, max_results=5)
            return videos
        except Exception as e:
            logger.error(f"Error in generate_youtube_links: {e}")
            return []

    def generate_full_party_json(self, party_input: PartyInput, product: Union[dict, list]) -> Dict[str, Any]:
        """Generate final structured party JSON for frontend."""
        if isinstance(product, list):
            if not product:
                return {"error": "Product data is empty. Please load products first."}
            product = product[0]  # safe now
        try:
            # 1️⃣ AI Party Plan
            party_json, suggested_gifts_list = self.generate_party_plan(party_input)
            print("gfparty--------------------",suggested_gifts_list)
           
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
            
            filtered_data = filter_data(product, party_input.budget)

            # 3️⃣ Detailed Gift Suggestions
            gifts_json = self.suggested_gifts(
                product_list=filtered_data,
                suggested_gifts=suggested_gifts_list,
                top_n=len(suggested_gifts_list),
            )
            print("giftjson---------------------",gifts_json)
            logger.info(f"Detailed Gifts JSON: {gifts_json}")

            
            
            return {
                "party_plan": new_party_ideas,
                "suggested_gifts": gifts_json,
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
    product = {
        "data": [
            {
                "id": "1",
                "title": "Superhero Cape",
                "description": "A cool superhero cape for kids.",
                "price": 20,
                "theme": "Superhero"
            },
            {
                "id": "2",
                "title": "Magic Wand",
                "description": "A magical wand for performing tricks.",
                "price": 15,
                "theme": "Magic"
            },
            {
                "id": "3",
                "title": "Treasure Chest",
                "description": "A treasure chest filled with goodies.",
                "price": 30,
                "theme": "Pirate"
            }
        ]
    }

    party_plan_generator = PartyPlanGenerator()
    full_party_json = party_plan_generator.generate_full_party_json(party_input, product)
    print("Full Party JSON:", json.dumps(full_party_json, indent=2))