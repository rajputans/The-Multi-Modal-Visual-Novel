"""MirAI Assignment 5 — Multi-Modal Visual Novel (Groq Edition)."""

import asyncio
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
import edge_tts


load_dotenv()
st.set_page_config(page_title="The Multi-Modal Visual Novel", page_icon="📖", layout="wide")

st.markdown(
    """<style>
    .stApp { background: radial-gradient(circle at 20% 0%, #25204a 0%, #11111d 45%, #08080e 100%); }
    h1, h2, h3 { color: #f5d78e !important; }
    div.stButton > button { border-radius: 12px; border: 1px solid #bf9c4a; padding: 0.65rem;
        background: linear-gradient(90deg, #34274e, #46305f); color: white; }
    div.stButton > button:hover { border-color: #f5d78e; color: #f5d78e; }
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def get_groq_client() -> Groq:
    """Cache the Groq client so Streamlit does not recreate it on each rerun."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from the .env file.")
    return Groq(api_key=api_key)


def director_prompt(genre: str, art_style: str, story_language: str) -> str:
    language_rule = "Write story_text and options in Hindi (Devanagari script)." if story_language == "Hindi" else "Write story_text and options in English."
    return f"""You are the director of a polished, family-friendly, choose-your-own-adventure visual novel.
Genre: {genre}. Requested visual art style: {art_style}.
{language_rule}

Your response must be ONLY one valid JSON object. Do not use Markdown, code fences, or commentary.
It must have exactly these keys:
- \"story_text\": a cinematic narrative paragraph of 80–120 words ending at a decision point.
- \"image_prompt\": a detailed ENGLISH prompt for an image generator. Include character appearance,
setting, action, lighting, atmosphere, camera composition, and {art_style}. State: no text, no logo,
no watermark, no speech bubbles.
- \"options\": a JSON array of 2 or 3 short, clearly different next actions in second person.

Continue the established plot faithfully. Do not mention that you are an AI or describe the JSON.
"""


def parse_scene(raw_text: str) -> dict:
    """Safely parse Groq's JSON response into a Python dictionary."""
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("No JSON object was received.")
    scene = json.loads(text[start : end + 1])
    required = {"story_text", "image_prompt", "options"}
    if set(scene) != required:
        raise ValueError("The response did not have the required JSON keys.")
    if not isinstance(scene["story_text"], str) or not isinstance(scene["image_prompt"], str):
        raise ValueError("Narrative or image prompt is invalid.")
    if not isinstance(scene["options"], list) or not 2 <= len(scene["options"]) <= 3:
        raise ValueError("There must be 2 or 3 story choices.")
    scene["options"] = [str(choice).strip() for choice in scene["options"] if str(choice).strip()]
    if not 2 <= len(scene["options"]) <= 3:
        raise ValueError("Story choices are empty.")
    return scene


def download_visual(image_prompt: str) -> bytes:
    """Generate and download the Pollinations visual for a scene."""
    url = f"https://image.pollinations.ai/prompt/{quote(image_prompt, safe='')}?width=768&height=432&nologo=true"
    response = requests.get(url, timeout=15, headers={"Accept": "image/*"})
    response.raise_for_status()
    if not response.headers.get("content-type", "").startswith("image/"):
        raise ValueError("Pollinations did not return an image.")
    return response.content


def selected_voice(story_language: str, voice_type: str) -> str:
    """Return a natural Microsoft Neural voice for the chosen language and gender."""
    voices = {
        ("English", "Female"): "en-IN-NeerjaNeural",
        ("English", "Male"): "en-IN-PrabhatNeural",
        ("Hindi", "Female"): "hi-IN-SwaraNeural",
        ("Hindi", "Male"): "hi-IN-MadhurNeural",
    }
    return voices[(story_language, voice_type)]


def create_audio(story_text: str, voice_name: str) -> bytes:
    """Create a natural-sounding MP3 using Microsoft Edge Neural Text-to-Speech."""
    async def collect_audio() -> bytes:
        audio = BytesIO()
        communicator = edge_tts.Communicate(story_text, voice_name, rate="+0%", pitch="+0Hz")
        async for chunk in communicator.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
        return audio.getvalue()

    return asyncio.run(collect_audio())


def generate_scene(player_move: str) -> bool:
    """Generate one scene; visual/audio problems never stop the story itself."""
    try:
        with st.spinner("✦ The director is shaping your next scene..."):
            messages = [
                {"role": "system", "content": director_prompt(st.session_state.genre, st.session_state.art_style, st.session_state.story_language)},
                *st.session_state.groq_conversation,
                {"role": "user", "content": player_move},
            ]
            result = get_groq_client().chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.85,
                max_tokens=550,
            )
            raw_response = result.choices[0].message.content or ""
            scene = parse_scene(raw_response)
    except Exception:
        st.toast("Story server is busy. Please choose again in a moment.", icon="⚠️")
        st.error("The next scene could not be created right now. Your current scene is safe.")
        return False

    # This persistent conversation list is Groq's stateful-chat equivalent.
    st.session_state.groq_conversation.extend([
        {"role": "user", "content": player_move},
        {"role": "assistant", "content": raw_response},
    ])
    st.session_state.chat_history.append({"move": player_move, "story": scene["story_text"]})

    # Visual and voice are independent network calls, so run both at the same time.
    # This makes a choice feel responsive instead of waiting for each task sequentially.
    scene["image_bytes"] = None
    scene["audio_bytes"] = None
    voice_name = selected_voice(st.session_state.story_language, st.session_state.voice_type)
    with ThreadPoolExecutor(max_workers=2) as executor:
        image_job = executor.submit(download_visual, scene["image_prompt"])
        audio_job = executor.submit(create_audio, scene["story_text"], voice_name)
        try:
            scene["image_bytes"] = image_job.result()
        except Exception:
            st.toast("Image server is busy, skipping visual...", icon="🖼️")
        try:
            scene["audio_bytes"] = audio_job.result()
        except Exception:
            st.toast("Narration service is busy, continuing without audio...", icon="🔊")

    st.session_state.current_scene = scene
    return True


def start_new_story() -> None:
    st.session_state.groq_conversation = []
    st.session_state.chat_history = []
    st.session_state.current_scene = None
    generate_scene("Begin a new adventure with a compelling cinematic opening scene.")


if "current_scene" not in st.session_state:
    st.session_state.current_scene = None
    st.session_state.groq_conversation = []
    st.session_state.chat_history = []
    st.session_state.genre = "Fantasy"
    st.session_state.art_style = "Cinematic digital painting"
    st.session_state.story_language = "English"
    st.session_state.voice_type = "Female"

with st.sidebar:
    st.title("⚙️ Story Settings")
    st.session_state.genre = st.selectbox("Story Genre", ["Fantasy", "Sci-Fi", "Mystery", "Adventure", "Horror"])
    st.session_state.art_style = st.selectbox("Art Style", ["Cinematic digital painting", "Anime", "Watercolor", "Pixel art", "Comic-book illustration"])
    st.session_state.story_language = st.selectbox("Story & narration language", ["English", "Hindi"])
    st.session_state.voice_type = st.selectbox("Narrator voice", ["Female", "Male"])
    if st.button("✦ Start new story", use_container_width=True):
        start_new_story()
    st.divider()
    st.caption(f"Scenes played: {len(st.session_state.chat_history)}")

st.title("📖 The Multi-Modal Visual Novel")

if st.session_state.current_scene is None:
    generate_scene("Begin a new adventure with a compelling cinematic opening scene.")

scene = st.session_state.current_scene
if scene:
    narrative_column, visual_column = st.columns([1.05, 1])
    with narrative_column:
        st.subheader("Current scene")
        st.write(scene["story_text"])
        if scene.get("audio_bytes"):
            st.caption("🔊 Narration")
            st.audio(scene["audio_bytes"], format="audio/mp3")
    with visual_column:
        if scene.get("image_bytes"):
            st.image(scene["image_bytes"], use_container_width=True)
        else:
            st.info("The story continues while its visual is unavailable.")

    st.subheader("What do you do next?")
    # Dynamic UI: each button is created from the parsed JSON options array.
    for index, option in enumerate(scene["options"]):
        button_key = f"choice_{len(st.session_state.chat_history)}_{index}"
        if st.button(option, key=button_key, use_container_width=True):
            # Clear feedback makes it obvious that the dynamically generated button was accepted.
            with st.spinner("Your choice was received — creating the next scene, visual and voice..."):
                created = generate_scene(option)
            if created:
                st.rerun()
