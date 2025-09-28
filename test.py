from app.services.party.party import PartyPlanGenerator
from app.schemas.schema import PartyInput, PartyDetails


#
product = PartyPlanGenerator()
#
#
# party_input = PartyInput(
#         person_name="Alice",
#         person_age=10,
#         budget=200.0,
#         num_guests=15,
#         party_date="2024-07-20",
#         location="Central Park",
#         party_details=PartyDetails(
#             theme="Superheroes",
#             favorite_activities=["painting", "outdoor games"]
#         )
#     )
#
# party_generate, gifts = product.generate_party_plan(party_input)
#
# print(gifts)

gift = ['Superhero Graphic Novel Series', 'Collectible Superhero Action Figure', 'DIY Comic Book Creation Kit', 'Personalized Superhero Cape', 'Art Supplies for Drawing Superheroes', 'Superhero-themed LEGO Set']

prod = [{'id': 'b0ca799e-6d10-4ee8-92e7-a942b68295a8',
  'title': ' edit edit Building Blocks',
  'description': 'A set of colorful blocks...',
  'product_type': 'GIFT',
  'age_range': '3-6 years',
  'avg_rating': 3.833333333333333,
  'theme': 'SUPERHERO',
  'price': 25.99},
 {'id': '382c826a-b4bc-4683-82fc-4d0fd66837b5',
  'title': 'Sparkle Horn Unicorn Plush',
  'description': 'Extra soft, large plush unicorn with a rainbow mane and shimmering horn. Great for cuddles.',
  'product_type': 'GIFT',
  'age_range': '3+ years',
  'avg_rating': 0,
  'theme': 'SUPERHERO',
  'price': 19.99},
 {'id': '0c8d5388-b45f-4e76-b155-9812a53d2435',
  'title': 'Little Chef Baking Set',
  'description': 'Child-safe, non-stick baking tools including mini-rolling pin, whisks, and cupcake molds.',
  'product_type': 'GIFT',
  'age_range': '5+ years',
  'avg_rating': 0,
  'theme': 'SUPERHERO',
  'price': 28.75},
 {'id': '05de1679-36db-4279-afa3-cb43ec4fa206',
  'title': ' Dig Excavation Kit',
  'description': 'Chisel and brush away plaster to excavate three different realistic dinosaur fossils.',
  'product_type': 'GIFT',
  'age_range': '6-10 years',
  'avg_rating': 0,
  'theme': 'SUPERHERO',
  'price': 22.99}]


top_n = 1

print(product.suggested_gifts(
    product=prod,
    suggest_gifts=gift,
    how_many=top_n
))