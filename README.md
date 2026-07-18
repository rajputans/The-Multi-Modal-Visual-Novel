# 📖 The Multi-Modal Visual Novel (Groq Edition)

An AI-powered interactive visual novel built with **Streamlit**, **Groq Llama 3.3 70B**, **Pollinations AI**, and **Microsoft Edge Text-to-Speech**.

Players make choices that dynamically shape the story while AI generates:

- 📚 Cinematic Story
- 🎨 AI-Generated Images
- 🎙️ Natural Voice Narration
- 🎮 Interactive Choices

---

# ✨ Features

- 🎭 Multiple Story Genres
  - Fantasy
  - Sci-Fi
  - Mystery
  - Adventure
  - Horror

- 🎨 Multiple Art Styles
  - Cinematic Digital Painting
  - Anime
  - Watercolor
  - Pixel Art
  - Comic Illustration

- 🌍 Language Support
  - English
  - Hindi

- 🎙️ AI Voice Narration
  - Male Voice
  - Female Voice

- 🤖 Powered by Groq Llama 3.3 70B

- 🖼️ Automatic Image Generation using Pollinations AI

- 📜 JSON-based Story Generation

- ⚡ Parallel Image + Audio Generation for faster performance

- 💾 Session-based Story Memory

---

# 🛠️ Tech Stack

| Technology | Purpose |
|------------|----------|
| Python | Backend |
| Streamlit | Web UI |
| Groq API | Story Generation |
| Llama 3.3 70B | AI Model |
| Pollinations AI | Image Generation |
| Edge TTS | AI Voice Narration |
| Requests | API Calls |
| dotenv | Environment Variables |

---

# 📂 Project Structure

```
.
│
├── app.py
├── requirements.txt
├── .env
├── README.md
└── assets/
```

---

# 📦 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/multimodal-visual-novel.git

cd multimodal-visual-novel
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=YOUR_API_KEY
```

Get your API Key from:

https://console.groq.com/keys

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your browser.

---

# 🎮 How to Play

1. Select your preferred Genre.
2. Select Art Style.
3. Choose Language.
4. Select Narrator Voice.
5. Click **Start New Story**.
6. Read the story.
7. Listen to AI narration.
8. View AI-generated artwork.
9. Choose one of the available actions.
10. Continue your adventure.

---

# 🧠 AI Workflow

```
User Choice
      │
      ▼
Groq Llama 3.3
      │
      ▼
JSON Scene
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Image     Audio
Generator Narration
 │         │
 └────┬────┘
      ▼
 Streamlit UI
```

---

# 📸 Screenshots

You can add screenshots here.

```
screenshots/

home.png

story.png

image_generation.png

voice.png
```

---

# 📚 Dependencies

- streamlit
- groq
- requests
- python-dotenv
- edge-tts

---

# 🚀 Future Improvements

- Save Story Progress
- User Authentication
- Character Memory
- Background Music
- Sound Effects
- Multiplayer Stories
- Story Export (PDF)
- Story Sharing
- Animated Characters
- More AI Models

---

# 🐞 Error Handling

The application gracefully handles:

- Invalid JSON responses
- API failures
- Missing images
- Audio generation failures
- Network issues
- Missing environment variables

---

# 👨‍💻 Author

**Ansh Singh**

B.Tech CSE Student

AI & Full Stack Developer

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ If you like this project

Give it a ⭐ on GitHub!

Happy Coding ❤️