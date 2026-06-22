import base64
import os
from datetime import datetime
from backend.prompt_service import build_character_prompt
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel

from backend.database import (
    clear_prompt_history,
    delete_prompt_history_item,
    get_prompt_history,
    initialize_database,
    save_prompt_history,
)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY was not loaded. Check your .env file.")
else:
    print("OPENAI_API_KEY loaded successfully.")


OUTPUT_FOLDER = "outputs"
REFERENCE_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "reference_images")
GENERATED_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "generated_images")

os.makedirs(REFERENCE_IMAGES_FOLDER, exist_ok=True)
os.makedirs(GENERATED_IMAGES_FOLDER, exist_ok=True)

initialize_database()


app = FastAPI(
    title="AI Game Character Generator API",
    version="1.0.0"
)


class CharacterPromptRequest(BaseModel):
    character_prompt: str
    companion_mood: str
    art_style: str
    environment: str
    enhancement: str
    reference_instruction: str


class HistoryRequest(BaseModel):
    character_prompt: str
    art_style: str
    environment: str
    enhancement: str
    reference_instruction: str
    reference_image_path: str | None = None
    generated_image_path: str | None = None
    image_status: str = "skipped"
    final_prompt: str


class ImageGenerationRequest(BaseModel):
    final_prompt: str


@app.get("/")
def home():
    return {
        "message": "AI Game Character Generator API is running."
    }


@app.get("/api-key-status")
def api_key_status():
    if os.getenv("OPENAI_API_KEY"):
        return {
            "status": "loaded"
        }

    return {
        "status": "missing"
    }


@app.post("/generate-prompt")
def generate_prompt(request: CharacterPromptRequest):
    final_prompt = build_character_prompt(request)

    return {
        "status": "success",
        "final_prompt": final_prompt
    }

@app.post("/save-history")
def save_history(request: HistoryRequest):
    save_prompt_history(request)

    return {
        "status": "success",
        "message": "Prompt history saved successfully."
    }


@app.get("/history")
def get_history():
    history = get_prompt_history(limit=10)

    return {
        "status": "success",
        "history": history
    }


@app.delete("/history")
def clear_history():
    clear_prompt_history()

    return {
        "status": "success",
        "message": "Prompt history cleared successfully."
    }


@app.delete("/history/{history_id}")
def delete_history_item(history_id: int):
    deleted_count = delete_prompt_history_item(history_id)

    if deleted_count == 0:
        return {
            "status": "not_found",
            "message": "History item not found."
        }

    return {
        "status": "success",
        "message": "History item deleted successfully."
    }


@app.post("/upload-reference")
def upload_reference(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = file.filename.split(".")[-1]
    file_name = f"reference_{timestamp}.{file_extension}"
    file_path = os.path.join(REFERENCE_IMAGES_FOLDER, file_name)

    image = Image.open(file.file)
    image.save(file_path)

    return {
        "status": "success",
        "reference_image_path": file_path
    }


@app.post("/generate-image")
def generate_image(request: ImageGenerationRequest):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"character_{timestamp}.png"
        file_path = os.path.join(GENERATED_IMAGES_FOLDER, file_name)

        result = client.images.generate(
            model="gpt-image-1",
            prompt=request.final_prompt,
            size="1024x1024"
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        with open(file_path, "wb") as image_file:
            image_file.write(image_bytes)

        return {
            "status": "success",
            "generated_image_path": file_path
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }