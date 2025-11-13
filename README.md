# 🎙️ Miss Riverwood – AI Voice Agent (Final Version)
**A bilingual, offline AI voice assistant for construction project updates — built for Riverwood Projects LLP.**

---

## 🧠 Project Overview
**Miss Riverwood** is a smart, friendly, bilingual (Hindi + English) AI Voice Assistant built as part of the **Riverwood AI Voice Agent Internship Challenge**.  
It simulates a real on-site assistant who understands user queries, analyzes them intelligently, and speaks back naturally in Hinglish.

The system supports both **voice and text interaction**, provides **real-time project updates**, and remembers context — all while running completely **offline**, ensuring **privacy, zero API cost**, and **fast response**.

---

## 🚀 Features

✅ Supports **Voice & Text input**  
✅ Understands **Hinglish (Hindi + English)** queries  
✅ Works **fully offline** – No cloud dependency  
✅ Uses **local LLM (Ollama)** for reasoning and response generation  
✅ Gives dynamic project updates (progress, materials, delays, safety, etc.)  
✅ Converts replies to speech using **gTTS**  
✅ Has editable project memory for real-time data simulation  
✅ Clean, dark-themed **Streamlit** UI  
✅ Remembers conversation context using session memory  

---
![Image1](https://github.com/vj220803/Riverwood_Voice_Agent_Ollama/blob/main/%F0%9F%A7%AD%20Miss%20Riverwood%20Voice%20Agent%20%E2%80%93%20Latest%20Flowchart%20-%20visual%20selection.png)
![Image1](https://github.com/vj220803/Riverwood_Voice_Agent_Ollama/blob/main/%F0%9F%A7%AD%20Miss%20Riverwood%20Voice%20Agent%20%E2%80%93%20Latest%20Flowchart%20-%20visual%20selection.png)
![Image1](https://github.com/vj220803/Riverwood_Voice_Agent_Ollama/blob/main/%F0%9F%A7%AD%20Miss%20Riverwood%20Voice%20Agent%20%E2%80%93%20Latest%20Flowchart%20-%20visual%20selection.png)
![Image2](https://github.com/vj220803/Riverwood_Voice_Agent_Ollama/blob/main/%F0%9F%A7%AD%20Miss%20Riverwood%20Voice%20Agent%20%E2%80%93%20Latest%20Flowchart%20-%20visual%20selection%20(1).png)


## 🧩 Project Flow (Simplified)

**User → Speech Input → Vosk (STT) → Ollama (LLM) → gTTS (TTS) → Streamlit UI Output**

1. The user speaks or types a message.  
2. If spoken, the **Vosk model** converts audio to text locally.  
3. The **Ollama Llama 3.2 model** analyzes the text and generates a Hinglish reply.  
4. The **gTTS engine** converts the reply into natural speech.  
5. The response is displayed and played through the **Streamlit interface**.  
6. **Session memory** keeps track of previous responses for contextual continuity.

---

## ⚙️ Tech Stack Used (Final Version)

| Component | Technology Used | Purpose |
|------------|------------------|----------|
| UI Framework | **Streamlit** | Lightweight and interactive web interface |
| Speech-to-Text | **Vosk (Offline Model)** | Converts Hindi/English voice to text |
| Reasoning Engine | **Ollama – Llama 3.2** | Generates Hinglish responses locally |
| Text-to-Speech | **gTTS** | Converts text responses into natural audio |
| Intent Detection | **RapidFuzz** | Detects query topics (progress, delay, safety, etc.) |
| Audio Handling | **PyDub + Wave** | Converts and manages recorded audio files |
| Memory | **Streamlit Session State** | Stores user history and editable project info |

---

## ❌ Technologies Not Used (and Why)

The original challenge document suggested several cloud-based tools — **Whisper (STT), OpenAI GPT API, Twilio Voice**, and **Cloud Hosting** — which were intentionally not used in the final version.

| Technology | Not Used Because | Replacement |
|-------------|------------------|--------------|
| **Whisper (STT)** | Required internet & heavy GPU for live transcription | Replaced with **Vosk (Offline STT)** |
| **OpenAI GPT API** | Depended on paid API keys & internet | Replaced with **Ollama Local LLM (Llama 3.2)** |
| **Twilio Voice / Phone Call** | Needed cloud setup, webhooks & paid plans | Replaced with **Browser Voice Input via Streamlit** |
| **Cloud Hosting (AWS/GCP)** | Expensive & unnecessary for local prototype | Runs **completely offline on local system** |

By removing external dependencies, the system became **faster, private, cost-free, and more reliable**.

---

## 🧩 Earlier Attempts & Challenges

This project went through multiple iterations before reaching the final stable version:

### 🧱 **Version 1 – Cloud-based Prototype**
- Used Whisper API and OpenAI GPT for reasoning.  
- Produced good responses but suffered from **high latency** and **API costs**.  
- Could not work offline and needed constant internet.  
❌ *Abandoned due to cost and delay.*

---

### 🌐 **Version 2 – Twilio + LangChain Integration**
- Attempted to integrate phone-call conversations using Twilio.  
- Required **webhook deployment** and **live server hosting**, making it complex for a local setup.  
- Audio quality and call handling were unstable.  
❌ *Abandoned due to infrastructure and setup complexity.*

---

### 💻 **Version 3 – Replit / Cloud IDE Setup**
- Tried running Streamlit and voice modules online using Replit.  
- Faced issues with **microphone input** and **audio file handling** due to platform limitations.  
❌ *Abandoned due to environment restrictions.*

---

### ✅ **Final Version – Local End-to-End System**
- Rebuilt fully in **Streamlit** with **local AI models** (Vosk + Ollama + gTTS).  
- Achieved **offline execution**, **low latency**, and **no dependency on external APIs**.  
- Fully aligns with Riverwood’s goals of privacy, practicality, and real-world usability.  
✅ *This is the version you see now.*

---

## 🧠 How It Meets Company Requirements

- **Conversational Flow:** Follows a complete voice assistant loop – STT → LLM → Memory → TTS → UI Output.  
- **Natural Hinglish Interaction:** Generates warm, bilingual responses ideal for Indian users.  
- **Personalization:** Stores user and project data for context-based answers.  
- **Offline & Low-Cost:** Runs fully locally with zero infrastructure cost.  
- **Realistic Simulation:** Uses editable project memory to simulate actual construction data.  
- **Fast Prototype:** Demonstrates quick, end-to-end implementation without relying on cloud APIs.

---

## ⚡ Why It Takes 4–5 Seconds to Respond

The response delay is natural because the system performs multiple steps:
1. Transcribing audio (Vosk)  
2. Reasoning using Llama 3.2 (Ollama)  
3. Generating voice via gTTS  
4. Updating Streamlit UI  

Future updates will **replace gTTS with a local TTS engine** and **use streaming responses**, reducing delay to 1–2 seconds.

---

## 🔗 Future Advancements

1. Replace gTTS with **Coqui TTS** or **Bark** for offline, expressive speech.  
2. Add **real-time streaming** for instant voice replies.  
3. Integrate **Whisper Tiny model** for faster speech recognition.  
4. Connect to **live company APIs or dashboards** for real-time project data.  
5. Add **multilingual support** (Marathi, Tamil, Gujarati).  
6. Introduce a **3D speaking avatar** for visual interactions.

---

## 🧮 Data and Memory System

Currently, project details are stored in a dictionary inside `app.py`:
```python
DEFAULT_PROJECT = {
  "project_name": "Riverwood Residences – Tower A",
  "overall_progress": "48%",
  "materials": {...},
  "delays": [...],

When Riverwood provides real data, this can easily connect to:
1. Excel or CSV files
2. Company APIs / Databases
3. Live site management tools
This allows Miss Riverwood to give authentic project updates directly from company systems.

### 🎯 Summary
Miss Riverwood is a bilingual AI Voice Assistant that runs 100% locally, understands Hinglish, and simulates real construction site conversations.
It’s private, fast, cost-free, and completely aligned with Riverwood’s challenge goals.

This final version reflects strong technical understanding, creativity, and system integration — delivering a real, practical conversational AI solution.

📹 Demo Link
🎥 Loom Video: https://www.loom.com/share/cc8ab40c58fb4c97b61446e8cac4fdc1

👩‍💻 Developed By
Vijayan Naidu
M.Sc. Data Science – Fergusson College (Autonomous), Pune
📧 venkatesh45naidu@gmail.com
🔗 https://www.linkedin.com/in/vijayan-naidu-ba9494330/
