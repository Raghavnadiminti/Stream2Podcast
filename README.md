# 🎧 Stream2Podcast

**Stream2Podcast** is an intelligent podcast-generation platform that converts YouTube videos into audio-based podcast episodes — and enhances the experience with a built-in **AI Assistant** that answers user questions mid-playback as spoken responses, then resumes the original podcast seamlessly.

---

## 🚀 Features

- 🔗 Convert any YouTube video into a podcast-style audio stream
- 🎧 Clean, minimal audio player with stream controls
- 🤖 **AI Ask Feature**
  - Ask a question at any time while listening
  - AI (powered by Google Gemini via LangChain) generates a relevant answer
  - Answer is converted to speech using `edge-tts` and streamed back to the player
  - Original podcast resumes automatically after response playback
- 📝 Automatic transcription using `youtube-transcript-api`
- 🔊 Voice synthesis with Microsoft Edge TTS for a natural response
- 💡 Fast and responsive frontend using React + Vite

---

## 🧠 How It Works

1. User pastes a YouTube URL
2. Backend fetches the transcript
3. Audio is streamed using `StreamingResponse`
4. When user asks a question:
   - The transcript is fed to an AI agent (LangChain + Gemini)
   - Response is generated and synthesized to speech
   - AI audio plays between the paused podcast
   - Podcast resumes after the answer

---

## 🛠️ Tech Stack

| Area           | Technology |
|----------------|------------|
| Frontend       | React.js, Vite, Axios, HTML5 Audio |
| Backend        | FastAPI, Uvicorn, CORS |
| AI/NLP         | Google Gemini (`google.generativeai`), LangChain |
| Speech Synthesis | `edge-tts` (Microsoft Edge TTS) |
| Transcription  | `youtube-transcript-api` |
| Audio Streaming| FastAPI `StreamingResponse`, `io.BytesIO` |
| Styling        | Custom CSS |

---

## 📁 Folder Structure
<pre>  
Stream2Podcast/
├── frontend/ # React frontend
│ ├── src/
│ │ ├── Podcast.jsx # Podcast player with Ask feature
│ │ ├── App.jsx # Root component
│ ├── index.html
│ ├── App.css # Global styles
│ ├── Podcast.css # Component-specific styles
│ ├── package.json # Frontend dependencies
│ └── vite.config.js # Vite configuration
│
├── backend/ # FastAPI backend
│ ├── main.py # FastAPI app + API routes
│ ├── podcast.py # AI agent logic, Gemini + TTS
│ ├── v2t.py # YouTube transcript extraction
│ └── requirements.txt # Python dependencies
│
├── .gitignore
└── README.md
</pre>
