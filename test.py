from app.services.t_shirt.shirt import TShirt
from app.utils.helper import response_data_img







t_shirt = TShirt(
    tshirt_type="Child",
    tshirt_size="M",
    gender="male",
    age="25",
    theme="princess",
    color="red"
)

# img_path = "data/ref.png"

# print("Generating Image......")
# response = t_shirt.generate_shirt_design(ref_img_path=img_path)
# print("Image Generated")
# response_data_img(response)


## Mockup
# desing_img_path = "data/generated_image.png"
#
# print("Generating Mockup......")
# response = t_shirt.generate_shirt_mockup(generated_design=desing_img_path)
# print("Mockup Generated")
# response_data_img(response)
