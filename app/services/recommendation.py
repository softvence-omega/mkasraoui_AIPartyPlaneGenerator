# app/services/recommendation.py
import requests
import json
import random
import re
from typing import List, Dict

from app.config import PRODUCT_API, GENAI_CLIENT, PRODUCT_MODEL
from google.genai import types


class RecommendationEngine:
    """AI-powered recommendation system for party products using Gemini."""
    
    def __init__(self, api_url: str = PRODUCT_API):
        self.api_url = api_url
    
    def fetch_products(self) -> List[Dict]:
        """Fetch all products from the API with limit=100000."""
        try:
            params = {"limit": 100000}
            response = requests.get(self.api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                # Extract items from the API response
                return data.get("data", {}).get("items", [])
            else:
                raise ValueError(f"Failed to fetch products. Status code: {response.status_code}")
        except Exception as e:
            raise ValueError(f"Error fetching products: {str(e)}")
    
    def get_ai_recommendations(
        self,
        theme: str,
        party_details: Dict,
        products: List[Dict],
        limit: int = 10
    ) -> List[Dict]:
        """
        Use Gemini AI to recommend products based on party details.
        
        Args:
            theme: Party theme
            party_details: Party details dict with theme and favorite_activities
            products: List of all available products
            limit: Number of recommendations to return
        
        Returns:
            List of recommended products with all fields
        """
        if not products:
            return []
        
        # Create a mapping of product IDs (as strings) to full product data for later retrieval
        product_map = {str(p.get("id")): p for p in products}
        
        # Prepare product catalog for the AI (limited fields for prompt)
        product_catalog = json.dumps([
            {
                "id": p.get("id"),
                "title": p.get("title"),
                "price": p.get("price"),
                "avg_rating": p.get("avg_rating"),
                "affiliated_company": p.get("affiliated_company"),
                "age_range": p.get("age_range")
            }
            for p in products[:1000]  # Use first 1000 products to avoid token limits
        ])
        
        # Build Gemini prompt
        activities = party_details.get("favorite_activities", [])
        activities_str = ", ".join(activities) if isinstance(activities, list) else str(activities)
        
        prompt = f"""
You are a party planning expert. Given party details and a product catalog, recommend the best products for this party.

Party Theme: {theme}
Party Activities: {activities_str}

Product Catalog (JSON):
{product_catalog}

Task:
1. Analyze the party theme and activities
2. From the product catalog provided, select the TOP {limit} most relevant products that would be perfect for this party
3. Return ONLY a JSON array with the product IDs of the recommended products
4. Products should match the theme and support the activities

Return ONLY the JSON array of product IDs, nothing else. Example format:
["id1", "id2", "id3"]
"""
        
        try:
            response = GENAI_CLIENT.models.generate_content(
                model= "gemini-2.5-flash",
                contents=[types.Part(text=prompt)]
            )

            # Extract and parse the response robustly
            if response.candidates:
                candidate = response.candidates[0]

                # Concatenate all parts to form the full response text
                candidate_text = ""
                if candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "text") and part.text:
                            candidate_text += part.text + "\n"
                candidate_text = candidate_text.strip()
                print("Raw AI response:", candidate_text)

                # Try to extract a JSON array anywhere in the response using regex,
                # fall back to parsing the whole text
                try:
                    # strip code fences if present
                    if candidate_text.startswith("```"):
                        inner = candidate_text.split("```", 2)[1]
                        if inner.strip().lower().startswith("json"):
                            candidate_text = inner.strip()[4:].strip()
                        else:
                            candidate_text = inner.strip()

                    # find first JSON array in text
                    match = re.search(r'\[.*?\]', candidate_text, re.S)
                    if match:
                        text = match.group(0)
                    else:
                        text = candidate_text

                    recommended_ids = json.loads(text)

                    # normalize to list of ids (strings)
                    if isinstance(recommended_ids, list):
                        normalized_ids = [str(x) for x in recommended_ids]

                        # Return full product objects from the map (keys are strings)
                        recommendations = [
                            product_map[pid] for pid in normalized_ids if pid in product_map
                        ]

                        if recommendations:
                            return recommendations[:limit]
                        else:
                            print("AI returned ids but none matched product catalog.")
                except json.JSONDecodeError:
                    print("Failed to parse JSON from AI response.")
                except Exception as e:
                    print("Unexpected error parsing AI response:", str(e))
        except Exception as e:
            print("="*100)
            print(f"Error getting AI recommendations: {str(e)}")
        
        print("No AI recommendations found or error occurred.")
        return []
    
    def recommend_products(
        self,
        theme: str,
        party_details: Dict,
        limit: int = 10
    ) -> Dict:
        """
        Main recommendation method: fetch products, use AI to recommend, and add random fallback if needed.
        
        Args:
            theme: Party theme
            party_details: Dict with theme and favorite_activities
            limit: Number of recommendations to return
        
        Returns:
            Dictionary with recommendations and metadata
        """
        # Fetch all products
        products = self.fetch_products()
        
        if not products:
            return {
                "theme": theme,
                "recommendations": [],
                "total_products_considered": 0,
                "recommendations_count": 0,
                "used_ai": True,
                "has_random_fallback": False,
            }
        
        # Get AI recommendations
        ai_recommendations = self.get_ai_recommendations(
            theme=theme,
            party_details=party_details,
            products=products,
            limit=limit
        )

        print("-"*100)
        print(ai_recommendations)
        print("-"*100)
        
        has_random_fallback = False
        
        # If AI didn't return enough recommendations, add random products
        if len(ai_recommendations) < limit:
            remaining = limit - len(ai_recommendations)
            ai_ids = {rec.get("id") for rec in ai_recommendations}
            
            # Get random products that weren't already recommended
            available_random = [p for p in products if p.get("id") not in ai_ids]
            random_products = random.sample(
                available_random,
                min(remaining, len(available_random))
            )
            
            ai_recommendations.extend(random_products)
            if random_products:
                has_random_fallback = True
        
        return {
            "theme": theme,
            "party_details": party_details,
            "recommendations": ai_recommendations[:limit],
            "total_products_considered": len(products),
            "recommendations_count": len(ai_recommendations[:limit]),
            "used_ai": True,
            "has_random_fallback": has_random_fallback,
        }
