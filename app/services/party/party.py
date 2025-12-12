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
from app.services.recommendation import RecommendationEngine

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


    def suggested_gifts(self, party_input: PartyInput, top_n: int = 20):
        """
        Generate gift recommendations using AI-powered recommendation engine.
        Recommends top_n products based on party theme and activities.
        If insufficient relevant products, adds random products as fallback.
        """
        try:
            logger.info(f"Generating gift suggestions for theme: {party_input.party_details.theme}")
            
            # Use the RecommendationEngine to get AI-powered recommendations
            engine = RecommendationEngine()
            
            party_details_dict = {
                "theme": party_input.party_details.theme,
                "favorite_activities": party_input.party_details.favorite_activities
            }
            
            recommendations = engine.recommend_products(
                theme=party_input.party_details.theme,
                party_details=party_details_dict,
                limit=top_n
            )
            
            logger.info(f"Generated {recommendations['recommendations_count']} gift recommendations")
            logger.info(f"Used fallback: {recommendations['has_random_fallback']}")
            
            return recommendations["recommendations"]

        except Exception as e:
            logger.error(f"Error in suggested_gifts: {e}")
            return []
        
        

    def generate_youtube_links(self, theme: str, age: int) -> List[dict]:
        """Fetch YouTube music/movie links for the party."""
        try:
            # Build a more specific query for better results
            query = f"{theme} party music songs for kids age {age}"
            logger.info(f"Searching YouTube videos with query: {query}")
            
            videos = search_youtube_videos(query, max_results=5)
            
            if not videos:
                logger.warning(f"No YouTube videos found for theme: {theme}, age: {age}")
                # Try with a simpler query as fallback
                logger.info("Trying fallback query...")
                fallback_query = f"{theme} party music"
                videos = search_youtube_videos(fallback_query, max_results=5)
            
            logger.info(f"Found {len(videos)} YouTube videos")
            return videos
        except Exception as e:
            logger.error(f"Error in generate_youtube_links: {e}")
            return []

    def generate_full_party_json(self, party_input: PartyInput, product: Union[dict, list]) -> Dict[str, Any]:
        """Generate final structured party JSON for frontend.

        If product data is missing or empty, the function will still generate the
        party plan and return an empty `suggested_gifts` list instead of raising
        an error. This keeps the `/party_generate` route functional even when
        product data failed to load at startup.
        """
        product_loaded = True
        # Normalize product argument and handle empty states gracefully
        if product is None:
            logger.warning("No product object provided. Proceeding without product data.")
            product_loaded = False
        elif isinstance(product, list):
            if not product:
                logger.warning("Product list is empty. Proceeding without product data.")
                product_loaded = False
            else:
                product = product[0]
        elif isinstance(product, dict):
            # If service assigned an empty dict or contains no items
            data_items = None
            try:
                data_items = product.get("data", {}).get("items")
            except Exception:
                data_items = None

            if not data_items:
                logger.warning("Product dict contains no items. Proceeding without product data.")
                product_loaded = False
        try:
            # 1️⃣ AI Party Plan
            party_json, suggested_gifts_list = self.generate_party_plan(party_input)
            # print("gfparty--------------------",suggested_gifts_list)
           
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

            # 3️⃣ AI-Powered Gift Recommendations (6 products with fallback to random)
            gifts_recommendations = self.suggested_gifts(
                party_input=party_input,
                top_n=6
            )
            # print("giftjson---------------------",gifts_recommendations)
            logger.info(f"Detailed Gifts Recommendations: {gifts_recommendations}")

            
            
            # Ensure we always return an array for suggested gifts, even if empty
            if not gifts_recommendations:
                gifts_recommendations = []

            return {
                "party_plan": new_party_ideas,
                "suggested_gifts": gifts_recommendations,
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