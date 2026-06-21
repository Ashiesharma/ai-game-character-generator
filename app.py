import os

import requests
import streamlit as st
from PIL import Image


DATA_FOLDER = "data"
OUTPUT_FOLDER = "outputs"
GENERATED_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "generated_images")
REFERENCE_IMAGES_FOLDER = os.path.join(OUTPUT_FOLDER, "reference_images")

HISTORY_FILE = os.path.join(DATA_FOLDER, "history.csv")
API_URL = "http://127.0.0.1:8000"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(GENERATED_IMAGES_FOLDER, exist_ok=True)
os.makedirs(REFERENCE_IMAGES_FOLDER, exist_ok=True)


def check_api_health():
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def generate_prompt_with_api(
    character_prompt,
    companion_mood,
    art_style,
    environment,
    enhancement,
    reference_instruction
):
    payload = {
        "character_prompt": character_prompt,
        "companion_mood": companion_mood,
        "art_style": art_style,
        "environment": environment,
        "enhancement": enhancement,
        "reference_instruction": reference_instruction
    }

    response = requests.post(f"{API_URL}/generate-prompt", json=payload, timeout=30)
    response.raise_for_status()

    return response.json()["final_prompt"]


def save_history_with_api(
    character_prompt,
    art_style,
    environment,
    enhancement,
    reference_instruction,
    reference_image_path,
    generated_image_path,
    image_status,
    final_prompt
):
    payload = {
        "character_prompt": character_prompt,
        "art_style": art_style,
        "environment": environment,
        "enhancement": enhancement,
        "reference_instruction": reference_instruction,
        "reference_image_path": reference_image_path,
        "generated_image_path": generated_image_path,
        "image_status": image_status,
        "final_prompt": final_prompt
    }

    response = requests.post(f"{API_URL}/save-history", json=payload, timeout=30)
    response.raise_for_status()

    return response.json()


def get_history_with_api():
    response = requests.get(f"{API_URL}/history", timeout=30)
    response.raise_for_status()

    return response.json()["history"]


def clear_history_with_api():
    response = requests.delete(f"{API_URL}/history", timeout=30)
    response.raise_for_status()

    return response.json()


def upload_reference_with_api(reference_image):
    if reference_image is None:
        return None

    reference_image.seek(0)

    files = {
        "file": (
            reference_image.name,
            reference_image,
            reference_image.type
        )
    }

    response = requests.post(f"{API_URL}/upload-reference", files=files, timeout=30)
    response.raise_for_status()

    return response.json()["reference_image_path"]


def generate_image_with_api(final_prompt):
    payload = {
        "final_prompt": final_prompt
    }

    response = requests.post(f"{API_URL}/generate-image", json=payload, timeout=120)
    response.raise_for_status()

    return response.json()


def create_character_summary(character_prompt, art_style, environment, enhancement):
    return f"""
Character concept created from your brief.

Style: {art_style}
Environment: {environment}
Creative direction: {enhancement}

Core idea:
{character_prompt}
"""


def get_companion_message(art_style):
    messages = {
        "Fantasy RPG": "The old realm is listening. Tell me the hero, villain, or creature you want to bring to life.",
        "Cyberpunk": "Neon systems online. Let's forge a character built for the streets of tomorrow.",
        "Anime": "Let's create someone with main-character energy and a design people remember.",
        "Pixel Art": "Small pixels, big legend. Describe the character and I'll shape the sprite-worthy idea.",
        "Dark Fantasy": "The shadows are ready. Give me a cursed knight, fallen angel, monster, or myth.",
        "Sci-Fi": "Star engines warmed up. Let's design a character from another world.",
        "3D Game Concept Art": "I'll think in silhouettes, materials, and production-ready details.",
        "Soft Aesthetic": "Let's make something dreamy, polished, and emotionally beautiful.",
        "Ethereal Fantasy": "Mist, glow, and magic are ready. Tell me what kind of being should appear.",
        "Pastel Moodboard": "Soft colors, curated mood, and gentle visual charm. Let's shape the concept.",
        "Cinematic Concept Art": "Let's build a character that feels like they belong in a full game trailer.",
        "Dark Academia Fantasy": "Old libraries, secret magic, and elegant mystery. Who are we creating?",
        "Cozy Magical": "Warm light, gentle magic, and charm. Let's create someone comforting and memorable.",
        "Y2K Cyber Fantasy": "Chrome, sparkle, neon, and attitude. Let's make a character with digital-era magic."
    }

    return messages.get(art_style, "What kind of game character are we creating today?")


st.set_page_config(
    page_title="AI Game Character Generator",
    page_icon="🎮",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #14131f 0%, #20243a 45%, #243b35 100%);
        color: #f5f7ff;
    }

    h1, h2, h3, p, label {
        color: #f5f7ff !important;
    }

    [data-testid="stTextArea"] textarea {
        background-color: #f8f8ff;
        color: #111111;
        border-radius: 10px;
        border: 1px solid #8f87ff;
        font-size: 16px;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #6b6b7a;
        opacity: 1;
    }

    [data-testid="stSelectbox"] div {
        color: #111111;
    }

    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.08);
        padding: 14px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .stButton button {
        background-color: #7c5cff;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 22px;
        font-weight: 600;
    }

    .stButton button:hover {
        background-color: #9b82ff;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

if "companion_mood" not in st.session_state:
    st.session_state.companion_mood = "Mysterious"

if "selected_art_style" not in st.session_state:
    st.session_state.selected_art_style = "Fantasy RPG"

if "selected_environment" not in st.session_state:
    st.session_state.selected_environment = "Mystic Forest"

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0


@st.dialog("Set Up Your Creative Companion")
def setup_companion():
    st.write("Choose the mood, world, and art direction for your helping companion.")

    companion_mood = st.selectbox(
        "Companion mood",
        ["Mysterious", "Friendly", "Epic", "Dark", "Cute", "Futuristic", "Magical"]
    )

    art_style_choice = st.selectbox(
        "Art style",
        [
            "Fantasy RPG",
            "Cyberpunk",
            "Anime",
            "Pixel Art",
            "Dark Fantasy",
            "Sci-Fi",
            "3D Game Concept Art",
            "Soft Aesthetic",
            "Ethereal Fantasy",
            "Pastel Moodboard",
            "Cinematic Concept Art",
            "Dark Academia Fantasy",
            "Cozy Magical",
            "Y2K Cyber Fantasy"
        ]
    )

    environment_choice = st.selectbox(
        "Environment",
        [
            "Mystic Forest",
            "Neon City",
            "Ancient Castle",
            "Space Station",
            "Desert Ruins",
            "Underwater Kingdom",
            "Battle Arena",
            "Dreamy Cloud Realm",
            "Vintage Library",
            "Moonlit Lake",
            "Cozy Witch Cottage",
            "Floating Island",
            "Glowing Flower Garden",
            "Rainy Neon Street",
            "Crystal Cave"
        ]
    )

    if st.button("Start Creating"):
        st.session_state.companion_mood = companion_mood
        st.session_state.selected_art_style = art_style_choice
        st.session_state.selected_environment = environment_choice
        st.session_state.setup_complete = True
        st.rerun()


if not st.session_state.setup_complete:
    setup_companion()


with st.sidebar:
    api_is_running = check_api_health()

    if api_is_running:
        st.success("API connected")
    else:
        st.error("API not running")

    st.header("Current Setup")

    st.write(f"Companion mood: {st.session_state.companion_mood}")
    st.write(f"Art style: {st.session_state.selected_art_style}")
    st.write(f"Environment: {st.session_state.selected_environment}")

    if st.button("Change Companion Setup"):
        st.session_state.setup_complete = False
        st.rerun()

    st.divider()
    st.header("Prompt History")

    try:
        history = get_history_with_api()

        if not history:
            st.info("No prompt history yet.")
        else:
            for row in history[:5]:
                title = f"{row['art_style']} - {row['environment']}"

                with st.expander(title):
                    st.caption(row["created_at"])
                    st.write(row["character_prompt"])

                    if row.get("enhancement"):
                        st.caption(f"Direction: {row['enhancement']}")

                    if row.get("reference_instruction"):
                        st.caption(f"Reference: {row['reference_instruction']}")

                    if row.get("reference_image_path"):
                        st.caption(f"Reference image: {row['reference_image_path']}")

                    if row.get("generated_image_path"):
                        st.caption(f"Generated image: {row['generated_image_path']}")

                    if row.get("image_status"):
                        st.caption(f"Image status: {row['image_status']}")

    except requests.exceptions.RequestException:
        st.warning("History is unavailable because the API is not running.")


st.title("AI Game Character Generator")

st.markdown(
    """
    <p style="font-size: 18px; color: #dfe4ff; margin-top: -8px;">
        Design game-ready characters using prompts, styles, environments, and visual references.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

st.subheader("Create Your Character")

art_style = st.session_state.selected_art_style
environment = st.session_state.selected_environment

st.markdown(
    f"""
    <div style="
        padding: 20px;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 22px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
    ">
        <h3 style="margin-bottom: 8px; color: #ffffff;">Your AI Creative Companion</h3>
        <p style="font-size: 17px; margin-bottom: 0; color: #dfe4ff;">
            {get_companion_message(art_style)}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

character_prompt = st.text_area(
    "Describe your character",
    placeholder="Example: A mysterious cyberpunk assassin with glowing blue eyes and a silver mask",
    key=f"character_prompt_input_{st.session_state.reset_counter}"
)

enhancement = st.radio(
    "Choose a creative direction",
    [
        "Balanced",
        "More cinematic",
        "More mysterious",
        "More cute",
        "More powerful",
        "More realistic",
        "More magical"
    ],
    horizontal=True
)

reference_instruction = "No reference image provided."

reference_image = st.file_uploader(
    "Upload a reference image optional",
    type=["png", "jpg", "jpeg"]
)

if reference_image is not None:
    image = Image.open(reference_image)
    st.image(image, caption="Reference Image", use_container_width=True)

    reference_instruction = st.text_area(
        "How should the reference image guide the character?",
        placeholder="Example: Use the glowing blue mood and soft magical lighting from this image, but create a completely new character.",
        height=90,
        key=f"reference_instruction_input_{st.session_state.reset_counter}"
    )

    if reference_instruction.strip() == "":
        reference_instruction = "Use the uploaded reference image as general visual inspiration without copying it directly."


if character_prompt.strip():
    try:
        final_prompt = generate_prompt_with_api(
            character_prompt,
            st.session_state.companion_mood,
            art_style,
            environment,
            enhancement,
            reference_instruction
        )
    except requests.exceptions.RequestException:
        final_prompt = "Could not connect to the API. Please make sure the FastAPI server is running."
else:
    final_prompt = "Write a character description to preview the generated prompt."


with st.expander("Prompt Preview"):
    st.write(final_prompt)

st.download_button(
    label="Download Prompt",
    data=final_prompt,
    file_name="character_prompt.txt",
    mime="text/plain"
)

generate_image_now = st.checkbox(
    "Generate image now",
    value=False,
    help="Leave this off to save credits while testing the app."
)

button_col1, button_col2 = st.columns([1, 1])

with button_col1:
    generate_clicked = st.button("Generate Character")

with button_col2:
    clear_clicked = st.button("Clear Inputs")

if generate_clicked:
    if character_prompt.strip() == "":
        st.warning("Please describe your character first.")
    elif final_prompt.startswith("Could not connect"):
        st.error("The API is not running. Start FastAPI first, then try again.")
    else:
        reference_image_path = upload_reference_with_api(reference_image)

        generated_image_path = None
        image_result = {
            "status": "skipped",
            "message": "Image generation was skipped."
        }

        if generate_image_now:
            image_result = generate_image_with_api(final_prompt)

            if image_result.get("status") == "success":
                generated_image_path = image_result["generated_image_path"]

        image_status = image_result.get("status", "unknown")

        save_history_with_api(
            character_prompt,
            art_style,
            environment,
            enhancement,
            reference_instruction,
            reference_image_path,
            generated_image_path,
            image_status,
            final_prompt
        )

        character_summary = create_character_summary(
            character_prompt,
            art_style,
            environment,
            enhancement
        )

        st.success("Character concept generated and saved.")

        if reference_image_path:
            st.caption(f"Reference image saved: {reference_image_path}")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("Character Result")

            if image_result.get("status") == "success":
                st.image(
                    generated_image_path,
                    caption="Generated Character",
                    use_container_width=True
                )
            elif image_result.get("status") == "skipped":
                st.info("Image generation skipped. Prompt and concept were saved.")
            else:
                st.warning("Image generation is currently unavailable.")
                st.caption(image_result.get("message", "No error details available."))

        with col2:
            st.subheader("Character Summary")
            st.write(character_summary)

        with st.expander("Generated Prompt"):
            st.write(final_prompt)

if clear_clicked:
    st.session_state.reset_counter += 1
    st.session_state.setup_complete = False
    st.rerun()