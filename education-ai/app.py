import streamlit as st
from google import genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="EduAgent AI", page_icon="🎓", layout="wide")

# --- 2. CSS STYLING (Neurovia-inspired dark orb aesthetic) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #060d10 !important;
    color: #e0eef2 !important;
    font-family: 'Sora', sans-serif !important;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(6, 18, 22, 0.95) !important;
    border-right: 1px solid rgba(0,210,180,0.12) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * {
    font-family: 'Sora', sans-serif !important;
    color: #8eb8c0 !important;
}
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #00d4b4 !important;
    font-size: 1rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .sidebar-stat-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #3e6470 !important;
}
[data-testid="stSidebar"] .sidebar-stat-value {
    font-size: 0.85rem;
    color: #00d4b4 !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stSidebarContent"] {
    padding: 2rem 1.5rem !important;
}

/* ── Main container ── */
[data-testid="stMain"] {
    background: transparent !important;
}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Navbar ── */
.edu-navbar {
    position: sticky;
    top: 0;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 3rem;
    background: rgba(6, 13, 16, 0.85);
    backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(0,210,180,0.08);
}
.edu-navbar-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #e0eef2;
    letter-spacing: 0.02em;
}
.edu-navbar-logo-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #00d4b4;
    box-shadow: 0 0 10px #00d4b4, 0 0 22px rgba(0,212,180,0.4);
    animation: pulse-dot 2.4s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.7; }
}
.edu-navbar-links {
    display: flex;
    gap: 2.5rem;
    list-style: none;
}
.edu-navbar-links a {
    color: #5a8a96;
    text-decoration: none;
    font-size: 0.82rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    transition: color 0.2s;
}
.edu-navbar-links a:hover { color: #00d4b4; }
.edu-navbar-cta {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.edu-navbar-badge {
    font-size: 0.72rem;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    border: 1px solid rgba(0,212,180,0.3);
    color: #00d4b4;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
    background: rgba(0,212,180,0.06);
}

/* ── Hero section ── */
.edu-hero {
    position: relative;
    min-height: 56vh;
    display: flex;
    align-items: center;
    padding: 2rem 3rem 2rem 3rem;
    overflow: hidden;
}

/* Glowing orb background */
.edu-orb {
    position: absolute;
    right: 4%;
    top: 50%;
    transform: translateY(-50%);
    width: 36vw;
    height: 36vw;
    max-width: 460px;
    max-height: 460px;
    border-radius: 50%;
    background: radial-gradient(circle at 38% 42%,
        rgba(0, 210, 180, 0.22) 0%,
        rgba(0, 140, 120, 0.14) 30%,
        rgba(0, 60, 80, 0.08) 60%,
        transparent 75%
    );
    box-shadow:
        inset 0 0 80px rgba(0,210,180,0.08),
        0 0 120px rgba(0,210,180,0.06),
        0 0 240px rgba(0,150,140,0.04);
    animation: orb-breathe 6s ease-in-out infinite;
    pointer-events: none;
}
.edu-orb::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1px solid rgba(0,210,180,0.12);
    animation: orb-ring 6s ease-in-out infinite;
}
.edu-orb::after {
    content: '';
    position: absolute;
    inset: 8%;
    border-radius: 50%;
    border: 1px solid rgba(0,210,180,0.06);
}
/* Particle dots inside orb */
.edu-orb-particles {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    overflow: hidden;
}
.edu-particle {
    position: absolute;
    width: 2px;
    height: 2px;
    background: #00d4b4;
    border-radius: 50%;
    opacity: 0;
    animation: particle-fade var(--dur, 3s) ease-in-out var(--delay, 0s) infinite;
}
@keyframes particle-fade {
    0%, 100% { opacity: 0; transform: scale(0.5); }
    50% { opacity: var(--op, 0.6); transform: scale(1); }
}
@keyframes orb-breathe {
    0%, 100% { transform: translateY(-50%) scale(1); }
    50% { transform: translateY(-50%) scale(1.04); }
}
@keyframes orb-ring {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

/* Ambient glow blobs */
.edu-glow-tl {
    position: absolute;
    top: -10%;
    left: -5%;
    width: 40vw;
    height: 40vw;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,100,120,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.edu-glow-br {
    position: absolute;
    bottom: -15%;
    right: 20%;
    width: 30vw;
    height: 30vw;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,60,80,0.07) 0%, transparent 70%);
    pointer-events: none;
}

/* ── Hero content ── */
.edu-hero-content {
    position: relative;
    z-index: 2;
    max-width: 52%;
}
.edu-hero-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00d4b4;
    margin-bottom: 1.4rem;
    font-family: 'DM Mono', monospace;
}
.edu-hero-title {
    font-size: clamp(2.4rem, 4.5vw, 4.2rem);
    font-weight: 700;
    line-height: 1.08;
    color: #e8f4f6;
    letter-spacing: -0.02em;
    margin-bottom: 1.4rem;
}
.edu-hero-title .accent {
    color: transparent;
    -webkit-text-stroke: 1px rgba(0,210,180,0.5);
}
.edu-hero-desc {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #4a7a86;
    max-width: 440px;
    margin-bottom: 2.8rem;
    font-weight: 300;
}

/* ── Feature pills (floating right of orb) ── */
.edu-hero-floats {
    position: absolute;
    right: 3%;
    top: 18%;
    z-index: 3;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.edu-float-pill {
    background: rgba(8, 22, 26, 0.82);
    border: 1px solid rgba(0,210,180,0.15);
    border-radius: 10px;
    padding: 0.7rem 1.1rem;
    backdrop-filter: blur(16px);
    text-align: right;
}
.edu-float-pill-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #b8d8df;
    letter-spacing: 0.04em;
}
.edu-float-pill-sub {
    font-size: 0.66rem;
    color: #3e6470;
    margin-top: 2px;
    font-family: 'DM Mono', monospace;
}

/* ── Input area ── */
.edu-input-section {
    position: relative;
    z-index: 2;
}

/* Override Streamlit text input */
[data-testid="stTextInput"] input {
    background: rgba(10, 26, 30, 0.9) !important;
    border: 1px solid rgba(0,210,180,0.2) !important;
    border-radius: 12px !important;
    color: #e0eef2 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 1rem !important;
    padding: 1rem 1.4rem !important;
    height: auto !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
    margin-bottom: 0 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,210,180,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,210,180,0.08), 0 0 20px rgba(0,210,180,0.06) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #2e5058 !important;
}
[data-testid="stTextInput"] label { display: none !important; }

/* ── Activate button ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,180,160,0.15) 0%, rgba(0,120,110,0.1) 100%) !important;
    border: 1px solid rgba(0,210,180,0.35) !important;
    border-radius: 10px !important;
    color: #00d4b4 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.58rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    margin-top: 0 rem !important;
   
    height: auto !important;
    width: auto !important;
   min-width: 160px !important;
    transition: all 0.25s ease !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
   
    display: block !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,210,180,0.22) 0%, rgba(0,160,140,0.16) 100%) !important;
    border-color: rgba(0,210,180,0.65) !important;
    box-shadow: 0 0 24px rgba(0,210,180,0.15), 0 0 48px rgba(0,210,180,0.06) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Bottom feature cards ── */
.edu-feature-cards {
    position: absolute;
    bottom: 6%;
    right: 4%;
    display: flex;
    gap: 0.8rem;
    z-index: 3;
}
.edu-feature-card {
    background: rgba(8, 22, 26, 0.85);
    border: 1px solid rgba(0,210,180,0.12);
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    backdrop-filter: blur(20px);
    min-width: 140px;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.edu-feature-card:hover {
    border-color: rgba(0,210,180,0.3);
    box-shadow: 0 0 20px rgba(0,210,180,0.06);
}
.edu-feature-card-icon {
    font-size: 1.2rem;
    margin-bottom: 0.4rem;
    display: block;
}
.edu-feature-card-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #b8d8df;
    display: block;
}
.edu-feature-card-sub {
    font-size: 0.65rem;
    color: #2e5058;
    font-family: 'DM Mono', monospace;
    margin-top: 2px;
    display: block;
}

/* ── Results section ── */
.edu-results-section {
    padding: 2rem 3rem 4rem;
    position: relative;
    z-index: 2;
}
.edu-section-label {
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #00d4b4;
    font-family: 'DM Mono', monospace;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.edu-section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,210,180,0.2), transparent);
}

/* Tabs override */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(0,210,180,0.1) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #3e6470 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 0 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #00d4b4 !important;
    border-bottom-color: #00d4b4 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 !important;
}

/* Status / spinner */
[data-testid="stStatusWidget"] {
    background: rgba(8, 22, 26, 0.9) !important;
    border: 1px solid rgba(0,210,180,0.15) !important;
    border-radius: 12px !important;
    color: #8eb8c0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* Markdown output */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #b8d8df !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    margin-top: 1.4rem !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #4a7a86 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.9rem !important;
    line-height: 1.8 !important;
}
[data-testid="stMarkdownContainer"] strong {
    color: #8eb8c0 !important;
}
[data-testid="stMarkdownContainer"] code {
    background: rgba(0,210,180,0.07) !important;
    color: #00d4b4 !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    padding: 0.1rem 0.4rem !important;
}

/* Text area (raw log) */
[data-testid="stTextArea"] textarea {
    background: rgba(6, 13, 16, 0.95) !important;
    border: 1px solid rgba(0,210,180,0.1) !important;
    border-radius: 10px !important;
    color: #2e6070 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.7 !important;
}
[data-testid="stTextArea"] label {
    color: #2e5058 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1px solid rgba(0,210,180,0.2) !important;
    border-radius: 8px !important;
    color: #00d4b4 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.76rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(0,210,180,0.07) !important;
    border-color: rgba(0,210,180,0.4) !important;
}

/* Warning / success */
[data-testid="stAlert"] {
    background: rgba(8, 22, 26, 0.9) !important;
    border-left: 3px solid #00d4b4 !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.85rem !important;
}

/* Divider */
hr {
    border-color: rgba(0,210,180,0.08) !important;
    margin: 1.5rem 0 !important;
}

/* Column gap fix */
[data-testid="column"] { padding: 0 0.3rem !important; align-items: center !important; display: flex !important; flex-direction: column !important; justify-content: center !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #060d10; }
::-webkit-scrollbar-thumb { background: rgba(0,210,180,0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,210,180,0.4); }
</style>
""", unsafe_allow_html=True)

# --- 3. BACKEND ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_ID = "gemini-3.1-flash-lite-preview"

def researcher_agent(topic):
    prompt = "You are a Researcher. Provide deep scientific facts about {topic}."
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

def writer_agent(raw_data):
    prompt = f"You are a Writer. Turn this into a professional study guide with structured headers and bullet points:\n{raw_data}"
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:2rem;">
        <div style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#1e4a54;font-family:'DM Mono',monospace;margin-bottom:1.2rem;">System Status</div>
        <div style="display:flex;flex-direction:column;gap:1rem;">
            <div>
                <div class="sidebar-stat-label">Model</div>
                <div class="sidebar-stat-value">Gemini 2.0 Flash</div>
            </div>
            <div>
                <div class="sidebar-stat-label">Mode</div>
                <div class="sidebar-stat-value">Multi-Agent</div>
            </div>
            <div>
                <div class="sidebar-stat-label">Latency</div>
                <div class="sidebar-stat-value">Ultra Low</div>
            </div>
            <div>
                <div class="sidebar-stat-label">Developer</div>
                <div class="sidebar-stat-value">Akshat Agrawal</div>
            </div>
        </div>
    </div>
    <div style="height:1px;background:rgba(0,210,180,0.08);margin:1.5rem 0;"></div>
    <div style="font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#1e4a54;font-family:'DM Mono',monospace;margin-bottom:1rem;">Agents Online</div>
    <div style="display:flex;flex-direction:column;gap:0.7rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.8rem;color:#4a7a86;font-family:'DM Mono',monospace;">
            <div style="width:6px;height:6px;border-radius:50%;background:#00d4b4;box-shadow:0 0 6px #00d4b4;flex-shrink:0;"></div>
            Researcher Agent
        </div>
        <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.8rem;color:#4a7a86;font-family:'DM Mono',monospace;">
            <div style="width:6px;height:6px;border-radius:50%;background:#00d4b4;box-shadow:0 0 6px #00d4b4;flex-shrink:0;"></div>
            Writer Agent
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. NAVBAR ---
st.markdown("""
<nav class="edu-navbar">
    <div class="edu-navbar-logo">
        <div class="edu-navbar-logo-dot"></div>
        EduAgent
    </div>
    <ul class="edu-navbar-links">
        <li><a href="#">Home</a></li>
        <li><a href="#">Agents</a></li>
        <li><a href="#">Docs</a></li>
    </ul>
    <div class="edu-navbar-cta">
        <span class="edu-navbar-badge">v2.0 · Live</span>
    </div>
</nav>
""", unsafe_allow_html=True)

# --- 6. HERO SECTION ---
# Orb with particle dots
particles_html = ""
import random
random.seed(42)
for i in range(60):
    x = random.randint(5, 95)
    y = random.randint(5, 95)
    op = round(random.uniform(0.2, 0.8), 2)
    dur = round(random.uniform(2.0, 5.5), 1)
    delay = round(random.uniform(0, 4.0), 1)
    size = random.choice([1, 1, 2, 2, 2, 3])
    particles_html += f'<div class="edu-particle" style="left:{x}%;top:{y}%;width:{size}px;height:{size}px;--op:{op};--dur:{dur}s;--delay:{delay}s;"></div>'

st.markdown(f"""
<section class="edu-hero">
    <div class="edu-glow-tl"></div>
    <div class="edu-glow-br"></div>
    <div class="edu-orb">
        <div class="edu-orb-particles">{particles_html}</div>
    </div>
    <div class="edu-hero-floats">
        <div class="edu-float-pill">
            <div class="edu-float-pill-title">Built with AI</div>
            <div class="edu-float-pill-sub">for maximum efficiency</div>
        </div>
        <div class="edu-float-pill">
            <div class="edu-float-pill-title">Smart Responses</div>
            <div class="edu-float-pill-sub">for every scenario</div>
        </div>
    </div>
    <div class="edu-hero-content">
        <div class="edu-hero-eyebrow">Multi-Agent Learning Solutions</div>
        <h1 class="edu-hero-title">
            Intelligent Study<br>
            <span class="accent">Automation</span>
        </h1>
        <p class="edu-hero-desc">
            Automate your learning with collaborative AI agents that research,
            synthesize, and format knowledge for any topic — in real-time.
        </p>
        <div class="edu-input-section" id="input-area"></div>
    </div>
    <div class="edu-feature-cards">
        <div class="edu-feature-card">
            <span class="edu-feature-card-icon">⬡</span>
            <span class="edu-feature-card-title">Real-Time</span>
            <span class="edu-feature-card-sub">Response</span>
        </div>
        <div class="edu-feature-card">
            <span class="edu-feature-card-icon">◈</span>
            <span class="edu-feature-card-title">Seamless</span>
            <span class="edu-feature-card-sub">Integration</span>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# --- 7. INPUT + BUTTON ---
st.markdown('<div style="display:flex;flex-direction:column;align-items:center;padding:1.5rem 3rem 0;">', unsafe_allow_html=True)

col_l, col_m, col_btn, col_r = st.columns([1, 3, 0.3, 1.7])
with col_m:
    topic = st.text_input(
        "",
        placeholder="Enter a topic — e.g., Deep Learning, Black Holes...",
        label_visibility="collapsed"
    )
with col_btn:
    submit_button = st.button("Submit")

st.markdown('</div>', unsafe_allow_html=True)

# --- 8. OUTPUT ---
if submit_button:
    if not topic:
        st.warning("Enter a topic above to initialize the agent network.")
    else:
        st.markdown('<div class="edu-results-section">', unsafe_allow_html=True)
        st.markdown('<div class="edu-section-label">Agent Output</div>', unsafe_allow_html=True)

        with st.status("⬡ Researcher Agent initializing...", expanded=True) as status:
            research_data = researcher_agent(topic)
            st.write("✦ Data harvested from knowledge base")
            st.write("◈ Handing off to Writer Agent...")
            time.sleep(0.8)
            final_output = writer_agent(research_data)
            status.update(label="✦ Process complete — output ready", state="complete", expanded=False)

        st.markdown("---")

        tab1, tab2 = st.tabs(["✦  Study Guide", "◈  Raw Data Log"])

        with tab1:
            st.success(f"Study guide generated for: **{topic.upper()}**")
            st.markdown(final_output)
            st.download_button(
                label="↓  Download as Markdown",
                data=final_output,
                file_name=f"{topic}_study_guide.md",
                mime="text/markdown"
            )

        with tab2:
            st.text_area("Agent logs:", research_data, height=320)

        st.markdown('</div>', unsafe_allow_html=True)
