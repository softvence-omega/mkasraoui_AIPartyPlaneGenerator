import os
from PIL import Image
from io import BytesIO
import mimetypes
import json
import cloudinary
from cloudinary.uploader import upload
import shutil
import requests

from app.config import CLOUDINARY_API_KEY, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_SECRET, GENERATED_IMG_PATH

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)


def cloudinary_file_upload(file_path):
    try:
        result = upload(
            file = file_path,
            resource_type = "auto",
            folder = "generated_images"
        )

        return result['secure_url']
    except Exception as e:
        raise ValueError(str(e))


def upload_image(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    return {"mime_type": mime_type, "data": image_data}

def response_data_img(response):
    os.makedirs(GENERATED_IMG_PATH, exist_ok=True)
    temp_file_path = os.path.join(GENERATED_IMG_PATH, "generated_image.png")

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(temp_file_path)
            # image.show()

    return temp_file_path


def load_json(json_data, JsonOpject):
    try:
        data_dict = json.loads(json_data)
        obj = JsonOpject(**data_dict)

        return obj
    except Exception as e:
        raise ValueError(str(e))

def delete_file(file_path):
    if os.path.exists(file_path):
        shutil.rmtree(file_path)



def request_product(url):
    response = requests.get(url)

    if response.status_code == 200:
        product = response.json()
        return product
    else:
        raise ValueError(f"Failed to fetch product. Status code: {response.status_code}")



def filter_data(data, price):

    filtered_items = [
        {
            "id" : item["id"],
            "title": item["title"],
            "description": item["description"],
            "product_type": item["product_type"],
            "age_range": item["age_range"],
            "avg_rating": item["avg_rating"],
            "theme": item["theme"],
            "price": item["price"]
        }
        for item in data["gifts"]
        if item["price"] <=price
    ]
    return filtered_items

