import base64
import os
from datetime import datetime

from PIL import Image


OUTPUT_FOLDER = "outputs"
REFERENCE_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "reference_images")
GENERATED_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "generated_images")

os.makedirs(REFERENCE_IMAGES_FOLDER, exist_ok=True)
os.makedirs(GENERATED_IMAGES_FOLDER, exist_ok=True)


def save_reference_image(file):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.split(".")[-1]
    file_name = f"reference_{timestamp}.{file_extension}"
    file_path = os.path.join(REFERENCE_IMAGES_FOLDER, file_name)

    image = Image.open(file.file)
    image.save(file_path)

    return file_path


def generate_character_image(client, final_prompt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"character_{timestamp}.png"
    file_path = os.path.join(GENERATED_IMAGES_FOLDER, file_name)

    result = client.images.generate(
        model="gpt-image-1",
        prompt=final_prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)

    return file_path