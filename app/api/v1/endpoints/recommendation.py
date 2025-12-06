# app/api/v1/endpoints/recommendation.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List

from app.services.recommendation import RecommendationEngine


router = APIRouter(prefix="/api/v1", tags=["recommendation"])


class PartyDetailsRequest(BaseModel):
    """Request model for party details."""
    theme: str
    favorite_activities: List[str]


@router.post("/recommendation")
async def get_product_recommendations(
    party_details: PartyDetailsRequest,
    limit: int = Query(10, ge=1, le=100, description="Number of recommendations to return")
):
    """
    Get AI-powered product recommendations based on party details.
    
    Uses Gemini AI to intelligently match products with party theme and activities.
    If insufficient similar products are found, adds random products as fallback.
    
    Args:
        party_details: Party details including theme and favorite_activities
        limit: Number of recommendations to return (default: 10, max: 100)
    
    Returns:
        JSON with:
        - theme: The theme used
        - party_details: The party details used for matching
        - recommendations: List of recommended products
        - total_products_considered: Total products in catalog
        - recommendations_count: Number of recommendations returned
        - used_ai: Whether AI was used
        - has_random_fallback: Whether random products were added due to insufficient matches
    """
    try:
        engine = RecommendationEngine()
        
        party_details_dict = {
            "theme": party_details.theme,
            "favorite_activities": party_details.favorite_activities
        }
        
        result = engine.recommend_products(
            theme=party_details.theme,
            party_details=party_details_dict,
            limit=limit
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")
