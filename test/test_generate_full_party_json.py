import json

from app.services.party.party import PartyPlanGenerator
from app.schemas.schema import PartyInput


def test_generate_full_party_json_with_empty_product(monkeypatch):
    # Prepare a sample PartyInput
    party_input = PartyInput(
        person_name="Test",
        person_age=8,
        budget=200,
        num_guests=10,
        party_date="2023-12-10",
        location="Testville",
        party_details={
            "theme": "Superhero",
            "favorite_activities": ["Treasure Hunt"]
        }
    )

    generator = PartyPlanGenerator()

    # Monkeypatch methods that call external APIs to avoid network calls
    monkeypatch.setattr(PartyPlanGenerator, "generate_party_plan", lambda self, x: (
        {
            "🎨 Theme & Decorations": ["Decor"],
            "🎉 Fun Activities": ["Fun"],
            "🍔 Food & Treats": ["Food"],
            "🛍️ Party Supplies": ["Supplies"],
            "⏰ Party Timeline": ["Timeline"],
            "🎁 Suggested Gifts": ["AI Gift 1", "AI Gift 2"]
        },
        ["AI Gift 1", "AI Gift 2"]
    ))
    monkeypatch.setattr(PartyPlanGenerator, "generate_youtube_links", lambda self, theme, age: [])
    monkeypatch.setattr(PartyPlanGenerator, "suggested_gifts", lambda self, party_input, top_n=20: [])

    # Test with empty product list
    result = generator.generate_full_party_json(party_input, [])

    assert isinstance(result, dict)
    assert "party_plan" in result
    assert isinstance(result.get("suggested_gifts"), list)
    assert result.get("suggested_gifts") == []


def test_generate_full_party_json_with_empty_product_dict(monkeypatch):
    party_input = PartyInput(
        person_name="Test",
        person_age=8,
        budget=200,
        num_guests=10,
        party_date="2023-12-10",
        location="Testville",
        party_details={
            "theme": "Superhero",
            "favorite_activities": ["Treasure Hunt"]
        }
    )

    generator = PartyPlanGenerator()

    monkeypatch.setattr(PartyPlanGenerator, "generate_party_plan", lambda self, x: (
        {
            "🎨 Theme & Decorations": ["Decor"],
            "🎉 Fun Activities": ["Fun"],
            "🍔 Food & Treats": ["Food"],
            "🛍️ Party Supplies": ["Supplies"],
            "⏰ Party Timeline": ["Timeline"],
            "🎁 Suggested Gifts": ["AI Gift 1", "AI Gift 2"]
        },
        ["AI Gift 1", "AI Gift 2"]
    ))
    monkeypatch.setattr(PartyPlanGenerator, "generate_youtube_links", lambda self, theme, age: [])
    monkeypatch.setattr(PartyPlanGenerator, "suggested_gifts", lambda self, party_input, top_n=20: [])

    product_dict = {"data": {"items": []}}

    result = generator.generate_full_party_json(party_input, product_dict)

    assert isinstance(result, dict)
    assert "party_plan" in result
    assert isinstance(result.get("suggested_gifts"), list)
    assert result.get("suggested_gifts") == []
