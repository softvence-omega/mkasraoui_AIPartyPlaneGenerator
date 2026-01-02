import google.generativeai as genai
from sympy import product
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ServiceUnavailable
import json
import time
import os
import threading
import concurrent.futures
from typing import List, Dict, Any, Union
from app.config import PRODUCT_MODEL, GEMINI_API_KEY, PARTY_PLANNER_PROMPT, PRODUCT_PROMPT
from app.utils.logger import get_logger
from app.schemas.schema import PartyInput
from app.services.party.adventure_list import search_youtube_videos
from app.utils.helper import filter_data
from app.services.recommendation import RecommendationEngine

logger = get_logger(__name__)


class PartyPlanGenerator:
    # In-memory caches to avoid repeated slow external calls
    _party_plan_cache = {}  # key -> (timestamp, (party_json, suggested_gifts))
    _party_plan_cache_lock = threading.Lock()
    _youtube_cache = {}  # key -> (timestamp, videos)
    _youtube_cache_lock = threading.Lock()
    PARTY_PLAN_CACHE_TTL = int(os.getenv("PARTY_PLAN_CACHE_TTL", "300"))  # seconds
    YOUTUBE_CACHE_TTL = int(os.getenv("YOUTUBE_CACHE_TTL", "3600"))  # seconds

    def _party_plan_cache_key(self, party_input: PartyInput) -> str:
        """Create a stable cache key for a party input."""
        key_data = {
            "person_name": party_input.person_name,
            "person_age": party_input.person_age,
            "budget": party_input.budget,
            "num_guests": party_input.num_guests,
            "party_date": party_input.party_date,
            "location": party_input.location,
            "theme": getattr(party_input.party_details, "theme", party_input.party_details.get("theme") if isinstance(party_input.party_details, dict) else None),
            "favorite_activities": getattr(party_input.party_details, "favorite_activities", party_input.party_details.get("favorite_activities") if isinstance(party_input.party_details, dict) else None)
        }
        return json.dumps(key_data, sort_keys=True, default=str)

    def _timed_call(self, name: str, func, *args, **kwargs):
        """Run func(*args, **kwargs) and log its duration. Returns func's result."""
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start
            logger.info(f"Task '{name}' completed in {duration:.3f}s")
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
        """Generate party plan JSON using AI with caching to avoid repeated slow calls."""
        key = self._party_plan_cache_key(party_input)
        # Try cache first
        with self._party_plan_cache_lock:
            entry = self._party_plan_cache.get(key)
            if entry and (time.time() - entry[0]) < self.PARTY_PLAN_CACHE_TTL:
                logger.info("Returning cached party plan")
                return entry[1]

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

            logger.info("Generating party plan (API call)...")
            client, config = self.model_client()
            response = self._make_api_call(client, PRODUCT_MODEL, party_prompt, config)
            raw_text = response.text.strip()
            party_json = json.loads(raw_text)

            # Extract suggested gifts
            suggested_gifts = party_json.get("🎁 Suggested Gifts", [])

            # Store in cache
            with self._party_plan_cache_lock:
                self._party_plan_cache[key] = (time.time(), (party_json, suggested_gifts))

            return party_json, suggested_gifts

        except Exception as e:
            logger.error(f"Error in generate_party_plan: {e}")
            raise e


    def suggested_gifts(self, party_input: PartyInput, top_n: int = 20):
        print("prinom")
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
        """Fetch YouTube music/movie links for the party with simple caching."""
        cache_key = f"yt:{theme}:{age}"
        with self._youtube_cache_lock:
            entry = self._youtube_cache.get(cache_key)
            if entry and (time.time() - entry[0]) < self.YOUTUBE_CACHE_TTL:
                logger.info("Returning cached YouTube results")
                return entry[1]

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

            with self._youtube_cache_lock:
                self._youtube_cache[cache_key] = (time.time(), videos)

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
            # Run three potentially slow operations in parallel to reduce overall latency
            logger.info("Starting parallel tasks: party plan, youtube links, gift recommendations")
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    "party": executor.submit(self._timed_call, "party", self.generate_party_plan, party_input),
                    "youtube": executor.submit(self._timed_call, "youtube", self.generate_youtube_links, party_input.party_details.theme, party_input.person_age),
                    "gifts": executor.submit(self._timed_call, "gifts", self.suggested_gifts, party_input, 6),
                }

                results = {}
                exceptions = {}

                for name, fut in futures.items():
                    try:
                        results[name] = fut.result()
                    except Exception as ex:
                        logger.error(f"Parallel task {name} failed: {ex}")
                        exceptions[name] = ex

            # If party plan failed, propagate the error (it's core to response)
            if "party" in exceptions:
                logger.error("Party plan generation failed in parallel execution; re-raising exception")
                raise exceptions["party"]

            # Extract results with sensible defaults
            party_json, suggested_gifts_list = results.get("party", ({}, []))
            logger.info(f"Party Plan JSON: {party_json}")

            new_party_ideas = {
                "🎨 Theme & Decorations": party_json.get("🎨 Theme & Decorations", []),
                "🎉 Fun Activities": party_json.get("🎉 Fun Activities", []),
                "🍔 Food & Treats": party_json.get("🍔 Food & Treats", []),
                "🛍️ Party Supplies": party_json.get("🛍️ Party Supplies", []),
                "⏰ Party Timeline": party_json.get("⏰ Party Timeline", [])
            }

            music_links = results.get("youtube", []) or []
            gifts_recommendations = results.get("gifts", []) or []

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