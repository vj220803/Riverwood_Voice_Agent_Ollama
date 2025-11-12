import os
import io
import json
import re
import wave
from pathlib import Path
from typing import Dict, List

import streamlit as st
import requests
from gtts import gTTS
from pydub import AudioSegment
from rapidfuzz import fuzz


# =========================================================
# CONFIG
# =========================================================
MODEL_DIR = Path("models")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_LLM = "llama3.2:1b"


# =========================================================
# PAGE + THEME
# =========================================================
st.set_page_config(
    page_title="Miss Riverwood – Free Local Voice Assistant",
    page_icon="🎙️",
    layout="wide",
)

# ENHANCED DARK THEME
st.markdown("""
<style>

:root {
  --ink:#e9eef4;
  --muted:#9db7c8;
  --green:#19c37d;
  --dark:#0b121b;
  --panel:#0f1824;
}

/* Background */
.stApp {
    background-color: var(--dark) !important;
    color: var(--ink) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] > div {
    background-color: #09111a !important;
}

/* Inputs */
input, textarea, select {
    background-color: #0f1824 !important;
    color: var(--ink) !important;
    border: 1px solid #1f2a36 !important;
}

/* Text area specific */
textarea {
    min-height: 120px !important;
    font-size: 1rem !important;
}

/* Buttons */
div.stButton > button {
    background-color: var(--green) !important;
    color: #002b18 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    height: 42px;
    transition: all 0.3s ease !important;
}

div.stButton > button:hover {
    background-color: #15a869 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(25,195,125,0.3);
}

/* Chips */
.badge {
    display:inline-block;
    padding:7px 12px;
    background: linear-gradient(90deg, rgba(25,195,125,.22), rgba(25,195,125,.10));
    border-radius:20px;
    margin:4px;
    border:1px solid rgba(255,255,255,.12);
    font-size:.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.badge:hover {
    background: linear-gradient(90deg, rgba(25,195,125,.35), rgba(25,195,125,.20));
    transform: scale(1.05);
}

/* Cards */
.card {
    background-color: #0f1824;
    padding:20px;
    border-radius:12px;
    border:1px solid rgba(255,255,255,.08);
    margin: 10px 0;
}

/* Success/Warning boxes */
.stSuccess, .stWarning, .stInfo {
    background-color: #0f1824 !important;
    border-radius: 8px !important;
}

/* Text colors */
.stMarkdown, .stText, .stCaption {
    color: var(--ink) !important;
}

/* Audio player */
.st-emotion-cache-1r6slb0 { color: var(--ink) !important; }

/* Expander */
.streamlit-expanderHeader {
    background-color: #0f1824 !important;
    border-radius: 8px !important;
}

hr { 
    border-color: rgba(255,255,255,.08);
    margin: 20px 0;
}

/* Section headers */
h3 {
    color: var(--green) !important;
    margin-top: 20px !important;
}

</style>
""", unsafe_allow_html=True)



# =========================================================
# DEFAULT PROJECT MEMORY
# =========================================================
DEFAULT_PROJECT = {
    "project_name": "Riverwood Residences – Tower A",
    "overall_progress": "48%",
    "milestones": [
        "Foundation and raft completed",
        "Ground + 3 slabs poured",
        "Blockwork up to Level 2 finished",
        "MEP rough-ins started at Level 1",
    ],
    "materials": {
        "cement": "Sufficient for next 10 days",
        "steel": "Next lot arriving tomorrow 11 AM",
        "bricks": "Stock for 7 days; fresh order placed",
        "tiles": "Shortlisted; vendor confirmation pending"
    },
    "delays": ["One-day slip due to heavy rain last week", "Tile vendor sample re-approval pending"],
    "safety": ["Daily toolbox talk at 9 AM", "PPE compliance at 97%", "Scaffold tag checks completed"],
    "team": {"site_engineer": "Asha Kulkarni", "contractor": "Rao Constructions", "electricians": 8, "masons": 24, "carpenters": 14},
    "next_steps": ["Slab shuttering for Level 4", "Brickwork Level 3", "Electrical conduits Level 2", "Lift shaft shuttering"],
    "site_hours": "Mon–Sat · 8:00–18:00",
    "contact": "site@riverwoodhomes.in · +91-98765-43210",
    "weather_note": "Light showers possible later today; concreting planned before 4 PM."
}



# =========================================================
# SESSION STATE INIT
# =========================================================
if "project_mem" not in st.session_state:
    st.session_state.project_mem = DEFAULT_PROJECT.copy()

if "chat_history" not in st.session_state:
    st.session_state.chat_history: List[Dict[str, str]] = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

if "show_transcription" not in st.session_state:
    st.session_state.show_transcription = False



# =========================================================
# AUDIO HELPERS
# =========================================================
def to_wav_16k(raw: bytes):
    audio = AudioSegment.from_file(io.BytesIO(raw))
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    return buf.getvalue()


@st.cache_resource(show_spinner=False)
def load_vosk_model(lang):
    from vosk import Model
    path = MODEL_DIR / (
        "vosk-model-small-hi-0.22" if lang == "hi"
        else "vosk-model-small-en-in-0.4"
    )
    return Model(str(path))


def transcribe_vosk(lang, wav_bytes):
    from vosk import KaldiRecognizer
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        rec = KaldiRecognizer(load_vosk_model(lang), wf.getframerate())
        text = ""
        while True:
            data = wf.readframes(4000)
            if not data: break
            if rec.AcceptWaveform(data):
                text += json.loads(rec.Result()).get("text", "") + " "
        text += json.loads(rec.FinalResult()).get("text", "")
    return text.strip()



def speak(text, lang="en"):
    tts = gTTS(text=text, lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()



# =========================================================
# INTENT ENGINE (improved fuzzy)
# =========================================================
STOP = set("the a an is are was were be been to for on in at from of with and or as what tell give show how when where who which do does can please kindly".split())

REPL = {
    "updation": "update",
    "constructions": "construction",
    "material": "materials",
    "safety update": "safety",
    "worksite": "site",
}

INTENTS = {
    "daily_update": ["construction update", "project update", "progress", "status", "what happened today"],
    "delays": ["delay", "blocked", "stuck", "issue"],
    "materials": ["materials", "cement", "steel", "brick", "tiles", "delivery"],
    "next_steps": ["next step", "tomorrow", "upcoming"],
    "team": ["team", "workforce", "workers"],
    "safety": ["safety", "ppe", "scaffold"],
    "weather": ["weather", "rain", "hot", "wind"],
    "percentage": ["percentage", "overall progress"],
    "contacts": ["contact", "reach"],
    "site_hours": ["site hours", "timings", "working hours"],
}


def normalize(t):
    t = t.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    for k, v in REPL.items(): t = t.replace(k, v)
    return " ".join([w for w in t.split() if w not in STOP])


def detect_intent(text):
    t = normalize(text)
    best, score = "daily_update", 0
    for intent, keys in INTENTS.items():
        for k in keys:
            sc = fuzz.partial_ratio(t, k)
            if sc > score:
                score, best = sc, intent
    return best



# =========================================================
# TEMPLATES
# =========================================================
def template_answer(intent, mem, lang):
    hi = (lang == "hi")

    if intent == "daily_update":
        return (
            f"{'नमस्ते!' if hi else 'Hello!'} "
            f"{'आज का अपडेट —' if hi else 'Here is today update —'} "
            f"{mem['project_name']} · {mem['overall_progress']} complete. "
            f"{mem['milestones'][0]}, {mem['milestones'][1]}. "
            f"{mem['weather_note']}"
        )

    if intent == "materials":
        m = mem["materials"]
        return f"Materials: Cement {m['cement']}, Steel {m['steel']}, Bricks {m['bricks']}, Tiles {m['tiles']}."

    if intent == "delays":
        return "Delays: " + ", ".join(mem["delays"]) if mem["delays"] else "No major delays."

    if intent == "team":
        t = mem["team"]
        return f"Team on site: {t['masons']} masons, {t['carpenters']} carpenters, {t['electricians']} electricians."

    if intent == "next_steps":
        return "Next steps: " + "; ".join(mem["next_steps"])

    if intent == "safety":
        return "Safety measures: " + "; ".join(mem["safety"])

    if intent == "weather":
        return mem["weather_note"]

    if intent == "percentage":
        return f"Overall progress: {mem['overall_progress']}"

    if intent == "contacts":
        return "Contact: " + mem["contact"]

    if intent == "site_hours":
        return "Site hours: " + mem["site_hours"]

    return template_answer("daily_update", mem, lang)



# =========================================================
# LLM GENERATION WITH MEMORY
# =========================================================
def generate_answer(user_text, lang):
    intent = detect_intent(user_text)
    draft = template_answer(intent, st.session_state.project_mem, lang)

    history = st.session_state.chat_history[-7:]
    history_text = "\n".join([f"{h['role']}: {h['content']}" for h in history])

    prompt = f"""
You are Miss Riverwood, a friendly bilingual (Hindi/English) site assistant.

Base memory:
{json.dumps(st.session_state.project_mem, ensure_ascii=False)}

Recent conversation:
{history_text}

User asked: {user_text}
Draft answer: {draft}

Give a polished, short, helpful answer in the SAME LANGUAGE as the user.
"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": DEFAULT_LLM, "prompt": prompt, "stream": False},
            timeout=60,
        ).json()

        final = r.get("response", draft)

    except:
        final = draft

    st.session_state.chat_history.append({"role": "user", "content": user_text})
    st.session_state.chat_history.append({"role": "assistant", "content": final})
    st.session_state.chat_history = st.session_state.chat_history[-12:]

    return final



# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Controls")

lang_choice = st.sidebar.selectbox("Speech / Reply Language", ["Indian English", "Hindi"])
lang_key = "hi" if lang_choice == "Hindi" else "en"

st.sidebar.text_input("Ollama LLM", DEFAULT_LLM)

with st.sidebar.expander("🧠 Project Memory (edit)", expanded=False):
    pm = st.session_state.project_mem
    pm["project_name"] = st.text_input("Project Name", pm["project_name"])
    pm["overall_progress"] = st.text_input("Overall Progress", pm["overall_progress"])
    pm["weather_note"] = st.text_area("Weather Note", pm["weather_note"])
    pm["site_hours"] = st.text_input("Site Hours", pm["site_hours"])
    pm["contact"] = st.text_input("Contact", pm["contact"])
    st.session_state.project_mem = pm

if st.sidebar.button("🔁 Reset conversation"):
    st.session_state.chat_history = []
    st.session_state.transcript = ""
    st.session_state.last_response = ""
    st.session_state.last_audio = None
    st.session_state.show_transcription = False
    st.rerun()



# =========================================================
# HEADER
# =========================================================
st.markdown("## 🎙️ Miss Riverwood – Free Local Voice Assistant")

with st.expander(" About Miss Riverwood & Riverwood Projects"):
    st.markdown("""
**Miss Riverwood** is a friendly bilingual (Hindi/English) AI voice agent for daily construction updates.  
She listens, transcribes (offline via **Vosk**), understands free-form queries (fuzzy intent), and speaks back.  
For open questions, she uses a completely **local LLM (Ollama)** — no cloud needed.

### **Challenge Objectives Met**
This prototype demonstrates:
1. **Casual bilingual greetings** (Hindi/English)
2. **Voice & Text input** support
3. **Contextual LLM responses** using Ollama (local)
4. **Human-like voice output** via gTTS
5. **Conversation memory** - remembers previous replies
6. **Construction updates simulation** with live project data

### **Riverwood Projects LLP**
- **Vision**: Building Foundations, Not Just Homes  
- **Specialty**: Plotted townships under DDJAY scheme (Haryana)  
- **Flagship**: Riverwood Estate, Sector 7, Kharkhauda (25 acres near IMT)  
- **Features**: 90–150 sq.m plots, 25,000 sq.ft clubhouse, vastu-compliant  
- **Founders**: Sanyam Chugh & Tarvinder Singh  

### **Technical Stack**
- **STT**: Vosk (offline, privacy-first)  
- **LLM**: Ollama llama3.2:1b (100% local)  
- **TTS**: gTTS (natural voice synthesis)  
- **Intent**: RapidFuzz fuzzy matching  
- **Framework**: Streamlit  

### 📞 **Contact**
**Radhika Goyal** (HR) · 8920418313 · radhika.goyal@riverwoodindia.com

""")


# Greeting
colg1, colg2 = st.columns([6,1])
with colg1:
    st.write("**Hi! I'm Miss Riverwood — your friendly site buddy. Speak or type in Hinglish/English; I'll respond fast and clearly.**")
with colg2:
    if st.button("▶️ Play Greeting"):
        greeting_audio = speak(
            "Namaste! Main Miss Riverwood hoon — aapke daily construction updates ki saathi. Aap Hindi ya English mix mein puch sakte ho, aur main turant jawab dungi.",
            "hi"
        )
        st.audio(greeting_audio, format="audio/mp3")



# =========================================================
# SUGGESTED QUERIES
# =========================================================
st.markdown("**Try these:** " + " ".join([
    f"<span class='badge'>{x}</span>" for x in [
        "What is the construction update today?",
        "Any delays or blockers?",
        "Materials delivery status?",
        "What are the next steps tomorrow?",
        "Team on site today?",
        "Safety updates?",
        "Weather impact today?",
        "Overall progress percentage?",
        "Contacts and site hours?"
    ]
]), unsafe_allow_html=True)

st.markdown("---")


# =========================================================
# MODE
# =========================================================
mode = st.selectbox("🔄 Mode", ["Voice", "Text"], label_visibility="collapsed")



# =========================================================
# VOICE MODE - FIXED WITH PROPER STATE MANAGEMENT
# =========================================================
if mode == "Voice":

    st.markdown("### 🎙️ Record your voice")
    audio_bytes = st.audio_input("Mic input")

    st.markdown("### 📝 Transcription")
    
    # Show transcription status
    if st.session_state.show_transcription and st.session_state.transcript:
        st.success(f"✅ Transcribed successfully!")
    
    # Editable text area - CRITICAL: No key, use default value from session state
    transcript_text = st.text_area(
        "You said (editable):",
        value=st.session_state.transcript,
        height=120,
        placeholder="Your transcribed text will appear here. You can also type or edit manually."
    )

    col1, col2 = st.columns([1,1])
    
    with col1:
        transcribe_btn = st.button("📝 Transcribe Voice", use_container_width=True)
        
    with col2:
        generate_btn = st.button("🤖 Generate Reply", use_container_width=True)
    
    # Handle transcription
    if transcribe_btn:
        if not audio_bytes:
            st.warning("⚠️ Please record something first.")
        else:
            with st.spinner("🎧 Transcribing your voice..."):
                try:
                    wav16 = to_wav_16k(audio_bytes.getvalue())
                    text = transcribe_vosk(lang_key, wav16)
                    
                    if text:
                        st.session_state.transcript = text
                        st.session_state.show_transcription = True
                        st.rerun()
                    else:
                        st.warning("⚠️ No speech detected. Please try again.")
                        
                except Exception as e:
                    st.error(f"❌ Transcription error: {str(e)}")

    # Handle reply generation
    if generate_btn:
        # Use the current value from the text area (which includes any manual edits)
        final_text = transcript_text.strip()
        
        if final_text == "":
            st.warning("⚠️ Please transcribe voice first or type text in the box above.")
        else:
            with st.spinner("🤔 Miss Riverwood is thinking..."):
                try:
                    # Update transcript with any manual edits
                    st.session_state.transcript = final_text
                    
                    # Generate response
                    final = generate_answer(final_text, lang_key)
                    st.session_state.last_response = final
                    
                    # Generate audio
                    audio_response = speak(final, "hi" if lang_key=="hi" else "en")
                    st.session_state.last_audio = audio_response
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Generation error: {str(e)}")
    
    # Display response if available
    if st.session_state.last_response:
        st.markdown("---")
        st.markdown("### ✅ Miss Riverwood says:")
        st.markdown(f"<div class='card'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
        
        if st.session_state.last_audio:
            st.audio(st.session_state.last_audio, format="audio/mp3")



# =========================================================
# TEXT MODE
# =========================================================
else:
    st.markdown("### ⌨️ Type your message")
    msg = st.text_input("Ask Miss Riverwood…", placeholder="e.g., What is the construction update today?")

    if st.button("🤖 Generate Reply", use_container_width=True):
        if msg.strip() == "":
            st.warning("⚠️ Please type something.")
        else:
            with st.spinner("🤔 Miss Riverwood is thinking..."):
                try:
                    final = generate_answer(msg.strip(), lang_key)
                    st.session_state.last_response = final
                    
                    audio_response = speak(final, "hi" if lang_key=="hi" else "en")
                    st.session_state.last_audio = audio_response
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Generation error: {str(e)}")
    
    # Display response if available
    if st.session_state.last_response:
        st.markdown("---")
        st.markdown("### ✅ Miss Riverwood says:")
        st.markdown(f"<div class='card'>{st.session_state.last_response}</div>", unsafe_allow_html=True)
        
        if st.session_state.last_audio:
            st.audio(st.session_state.last_audio, format="audio/mp3")


st.markdown("---")

# =========================================================
# CHAT HISTORY
# =========================================================
st.markdown("### 🗂️ Recent Conversation")

if not st.session_state.chat_history:
    st.caption("No previous messages yet.")
else:
    for h in st.session_state.chat_history[-7:]:
        icon = "👤" if h["role"] == "user" else "🤖"
        role_color = "#19c37d" if h["role"] == "assistant" else "#9db7c8"
        st.markdown(
            f"<div style='padding:8px; margin:5px 0; border-left:3px solid {role_color};'>"
            f"{icon} <strong>{h['role'].title()}:</strong> {h['content']}"
            f"</div>",
            unsafe_allow_html=True
        )



# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("""
🔒 **100% Local & Private** — Vosk STT (offline models in `models/`), gTTS voice synthesis, Ollama LLM (`llama3.2:1b`)  
🚀 **Quick Start:** `ollama serve` → `ollama pull llama3.2:1b` → `streamlit run app.py`  
💡 **Made for Riverwood Projects LLP** — Building Foundations, One Voice at a Time
""")