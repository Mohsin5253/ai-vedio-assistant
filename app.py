import streamlit as st
import time
from dotenv import load_dotenv

# Core imports remain untouched
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

# Auth and Avatar imports
from core.auth import register_user, login_user

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS (Production Level) ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* Apply smooth scrolling globally */
html, body, .stApp {
    scroll-behavior: smooth !important;
}

/* ── Root Variables ── */
:root {
    --bg: #09090b;
    --surface: rgba(24, 24, 27, 0.6);
    --surface-2: rgba(39, 39, 42, 0.7);
    --border: rgba(255, 255, 255, 0.1);
    --border-highlight: rgba(124, 58, 237, 0.4);
    --accent: #8b5cf6;
    --accent-glow: #a78bfa;
    --accent-2: #06b6d4;
    --text: #f4f4f5;
    --text-muted: #a1a1aa;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Glassmorphism Background */
.stApp::before {
    content: '';
    position: fixed;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 50% 50%, rgba(124, 58, 237, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.05) 0%, transparent 30%);
    pointer-events: none;
    z-index: 0;
}


/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    color: var(--text) !important;
    font-weight: 800 !important;
}

/* ── Hero Title ── */
.hero-title {
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent-glow) 50%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Glass Cards ── */
.card {
    background: var(--surface);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

.card:hover {
    border-color: var(--border-highlight);
    box-shadow: 0 8px 40px rgba(124, 58, 237, 0.15);
}



.card-title {
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.card-content {
    font-size: 0.95rem;
    line-height: 1.8;
    color: var(--text);
}

/* ── Accent Badge ── */
.badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    backdrop-filter: blur(10px);
}
.badge-purple { background: rgba(124,58,237,0.15); color: var(--accent-glow); border: 1px solid rgba(124,58,237,0.3); }
.badge-cyan   { background: rgba(6,182,212,0.15); color: var(--accent-2);    border: 1px solid rgba(6,182,212,0.3); }
.badge-green  { background: rgba(16,185,129,0.15); color: var(--success);    border: 1px solid rgba(16,185,129,0.3); }

/* ── Input & Buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 10px !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Fix browser autofill grey/yellow backgrounds */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active{
    -webkit-box-shadow: 0 0 0 30px #ffffff inset !important;
    -webkit-text-fill-color: #000000 !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.2) !important;
    background: rgba(124, 58, 237, 0.05) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
}

.stButton > button:hover {
    box-shadow: 0 8px 25px rgba(124,58,237,0.5) !important;
    background: linear-gradient(135deg, #9333ea, #7e22ce) !important;
}

/* Secondary button */
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: var(--text-muted) !important;
}

/* ── Progress / Status ── */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--surface-2);
    border-radius: 10px;
    margin: 0.5rem 0;
    border: 1px solid var(--border);
    font-size: 0.85rem;
}

.status-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-active   { background: var(--accent-glow); box-shadow: 0 0 12px var(--accent-glow); }
.dot-done     { background: var(--success); box-shadow: 0 0 8px var(--success); }
.dot-pending  { background: var(--border); }

/* ── Chat ── */
.chat-container {
    background: var(--surface);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 1.5rem;
}

.chat-msg {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.chat-label {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.chat-bubble {
    padding: 1rem 1.4rem;
    border-radius: 16px;
    font-size: 0.95rem;
    line-height: 1.6;
    max-width: 85%;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.user-label  { color: var(--accent-glow); }
.bot-label   { color: var(--accent-2); }

.user-bubble { 
    background: linear-gradient(135deg, #5b21b6, #4c1d95); 
    border: 1px solid rgba(124,58,237,0.4); 
    align-self: flex-end; 
    border-bottom-right-radius: 4px;
}
.bot-bubble  { 
    background: linear-gradient(135deg, #155e75, #0e7490); 
    border: 1px solid rgba(6,182,212,0.4);   
    align-self: flex-start; 
    border-bottom-left-radius: 4px;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── Transcript box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    font-size: 0.85rem;
    line-height: 1.8;
    max-height: 350px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Empty State ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 6rem 2rem;
    text-align: center;
}

/* ── Mobile Responsive ── */
@media (max-width: 768px) {
    .card { padding: 1rem !important; }
    .chat-bubble { max-width: 100% !important; padding: 0.85rem 1rem !important; font-size: 0.9rem !important; }
    .empty-state { padding: 3rem 1rem !important; }
    .hero-title { font-size: clamp(2rem, 8vw, 3rem) !important; }
    .hero-sub { font-size: 0.75rem !important; }
    .transcript-box { padding: 1rem !important; max-height: 250px !important; }
    [data-testid="stSidebar"] { min-width: 100vw !important; } /* Make sidebar full width on mobile */
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
    "user_authenticated": False,
    "username": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─── Auth Wall ───────────────────────────────────────────────────────────────────
if not st.session_state.user_authenticated:
    st.markdown('<div class="hero-title" style="text-align: center; margin-top: 5rem;">AI Video Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub" style="text-align: center; margin-bottom: 3rem;">Secure Login Required</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:

        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True):
                success, msg = login_user(login_username, login_password)
                if success:
                    st.session_state.user_authenticated = True
                    st.session_state.username = login_username
                    st.success(msg)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
                    
        with tab2:
            reg_username = st.text_input("New Username", key="reg_username")
            reg_password = st.text_input("New Password", type="password", key="reg_password")
            if st.button("Register", use_container_width=True):
                success, msg = register_user(reg_username, reg_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

    st.stop()

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_status(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active":  return "dot-active"
    if s == "done":    return "dot-done"
    return "dot-pending"

def render_step_bar(label: str, key: str, icon: str):
    css = step_status(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot {css}"></div>
        <span>{icon} {label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:2rem">🎬 AI<br>Video</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">Welcome, {st.session_state.username}</div>', unsafe_allow_html=True)
    
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.user_authenticated = False
        st.session_state.username = None
        st.rerun()
        


    st.markdown('<span class="badge badge-cyan">Input</span>', unsafe_allow_html=True)
    source = st.text_input("YouTube URL or File Path", placeholder="https://youtube.com/watch?v=...")

    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    run_btn = st.button("⚡ Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for step, icon, label in [
            ("audio",      "🔊", "Audio Processing"),
            ("transcript", "📝", "Transcription"),
            ("title",      "🏷️", "Title Generation"),
            ("summary",    "📋", "Summarisation"),
            ("extract",    "🔍", "Extraction"),
            ("rag",        "🧠", "RAG Engine"),
        ]:
            render_step_bar(label, step, icon)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("⚙️ Pipeline running — see sidebar for live status…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("✅ Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"❌ Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title banner
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-size:1.6rem;font-weight:800;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # Top row: summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card" style="height: 100%;">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Second row: action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">✅ Action Items</div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🔑 Key Decisions</div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">❓ Open Questions</div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-title" style="font-size:2rem;margin-bottom:1.5rem">💬 Chat with your Meeting</div>', unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">🤖 AI Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem">
            <div style="font-size:3rem;margin-bottom:1rem">💬</div>
            <div style="color:var(--text-muted);font-size:1rem;font-weight:600;">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([6, 1], gap="medium")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):

            answer = ask_question(r["rag_chain"], user_input.strip())
            
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:5rem;margin-bottom:1rem;text-shadow: 0 0 20px rgba(124,58,237,0.5);">🎬</div>
        <div class="hero-title" style="font-size: 2.5rem; margin-bottom:1rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:1.1rem;max-width:450px;line-height:1.8">
            Paste a YouTube URL or local file path in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:3rem;display:flex;gap:1rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Transcription</span>
            <span class="badge badge-cyan">Summarisation</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)