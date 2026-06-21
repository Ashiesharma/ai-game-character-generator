import base64
import os
from datetime import datetime
from openai import OpenAI
import pandas as pd
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY was not loaded. Check your .env file.")
else:
    print("OPENAI_API_KEY loaded successfully.")


DATA_FOLDER = "data"
OUTPUT_FOLDER = "outputs"
REFERENCE_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "reference_images")
GENERATED_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "generated_images")

HISTORY_FILE = os.path.join(DATA_FOLDER, "history.csv")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(REFERENCE_IMAGES_FOLDER, exist_ok=True)
os.makedirs(GENERATED_IMAGES_FOLDER, exist_ok=True)

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

def save_prompt_history(request: HistoryRequest):
    new_row = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "character_prompt": request.character_prompt,
        "art_style": request.art_style,
        "environment": request.environment,
        "enhancement": request.enhancement,
        "reference_instruction": request.reference_instruction,
        "reference_image_path": request.reference_image_path,
        "generated_image_path": request.generated_image_path,
        "image_status": request.image_status,
        "final_prompt": request.final_prompt
    }

    if os.path.exists(HISTORY_FILE):
        history_df = pd.read_csv(HISTORY_FILE)
        history_df = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        history_df = pd.DataFrame([new_row])

    history_df.to_csv(HISTORY_FILE, index=False)

@app.get("/")
def home():
    return {
        "message": "AI Game Character Generator API is running."
    }


@app.post("/generate-prompt")
def generate_prompt(request: CharacterPromptRequest):
    final_prompt = f"""
Create a game-ready character concept based on the following creative brief.

Character description:
{request.character_prompt}

Companion mood guiding the design:
{request.companion_mood}

Art direction:
{request.art_style}

World/environment influence:
{request.environment}

Creative direction:
{request.enhancement}

Reference image guidance:
{request.reference_instruction}

Design requirements:
- Use the art direction and environment to influence outfit, colors, lighting, materials, pose, and mood.
- Make the character visually unique and suitable for a game concept art pipeline.
- Include clear silhouette, readable costume details, and strong personality.
- If a reference image is provided, use it as inspiration according to the user's reference guidance without copying it directly.
- Avoid blurry details, extra limbs, broken anatomy, distorted hands, and unreadable face details.
- The final image should feel polished, intentional, and production-ready.
"""

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
    if not os.path.exists(HISTORY_FILE):
        return {
            "status": "success",
            "history": []
        }

    history_df = pd.read_csv(HISTORY_FILE)

    if history_df.empty:
        return {
            "status": "success",
            "history": []
        }

    history_df = history_df.fillna("")
    history = history_df.tail(10).iloc[::-1].to_dict(orient="records")

    return {
        "status": "success",
        "history": history
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

@app.delete("/history")
def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

    return {
        "status": "success",
        "message": "Prompt history cleared successfully."
    }