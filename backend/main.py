import os
from backend.prompt_service import build_character_prompt
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from openai import OpenAI
from pydantic import BaseModel
from backend.image_service import generate_character_image, save_reference_image

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
    file_path = save_reference_image(file)

    return {
        "status": "success",
        "reference_image_path": file_path
    }

@app.post("/generate-image")
def generate_image(request: ImageGenerationRequest):
    try:
        file_path = generate_character_image(client, request.final_prompt)

        return {
            "status": "success",
            "generated_image_path": file_path
        }

    except Exception as error:
        return {
            "status": "error",
            "message": str(error)
        }