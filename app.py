import streamlit as st
import io
import urllib.request
import re
from groq import Groq

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // MARK VII",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HUD Dark Cyberpunk Styling ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b1118;
        color: #00e5ff;
        font-family: 'Courier New', monospace;
    }
    .hud-header {
        border-bottom: 2px solid #00e5ff;
        padding-bottom: 8px;
        margin-bottom: 15px;
        text-shadow: 0 0 10px #00e5ff;
    }
    .status-card {
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid #00e5ff;
        border-radius: 4px;
        padding: 10px;
        margin: 5px 0;
    }
    .stButton>button {
        color: #00e5ff !important;
        border: 1px solid #00e5ff !important;
        background-color: rgba(0, 229, 255, 0.1) !important;
        font-family: 'Courier New', monospace;
    }
    .stButton>button:hover {
        background-color: #00e5ff !important;
        color: #0b1118 !important;
        box-shadow: 0 0 15px #00e5ff;
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(0, 229, 255, 0.03);
        border-left: 2px solid #00e5ff;
        border-radius: 4px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- J.A.R.V.I.S. Persona Instructions ---
SYSTEM_PROMPT = """
You are J.A.R.V.I.S., the AI assistant running Tony Stark's Mark VII Iron Man suit.
- Always address the user respectfully as 'Sir', 'Commander', or 'Mr. Stark'.
- Keep your tone witty, sophisticated, British-refined, and composed.
- Be concise, tactical, and helpful.
"""

# --- Session State Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Good day, sir. Systems are online and physical suit architecture modules are standing by. How may I be of assistance?"}
    ]

default_api_key = st.secrets.get("GROQ_API_KEY", "")
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = default_api_key

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True

if "last_reply_to_speak" not in st.session_state:
    st.session_state.last_reply_to_speak = ""

def play_browser_voice(text: str):
    clean_text = text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    snippet = ". ".join(clean_text.split(". ")[:2])
    speech_js = f"""
    <script>
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        let utterance = new SpeechSynthesisUtterance("{snippet}");
        utterance.rate = 1.0;
        utterance.pitch = 0.95;
        let voices = window.speechSynthesis.getVoices();
        let ukVoice = voices.find(v => v.lang.includes('en-GB') || v.name.includes('UK') || v.name.includes('British'));
        if (ukVoice) utterance.voice = ukVoice;
        window.speechSynthesis.speak(utterance);
    }}
    </script>
    """
    st.components.v1.html(speech_js, height=0)

def sandbox_url_inspect(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8', errors='ignore')
            title_search = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            return title_search.group(1).strip() if title_search else "HTTP 200 - OK (No title tag)"
    except Exception as e:
        return f"Status: Error - {str(e)}"

# --- SIDEBAR: Telemetry & Controls ---
with st.sidebar:
    st.markdown("### // PROTOCOLS & HARDWARE")
    st.markdown("""
    <div class='status-card'>
        <b>SUIT LINK:</b> STANDBY<br>
        <b>COGNITIVE ENGINE:</b> DUAL CORE<br>
        <b>MATH SOLVER:</b> ONLINE<br>
        <b>ACTUATOR BUS:</b> CAN-BUS READY<br>
        <b>ROBOTICS OS:</b> ROS2 COMPLIANT<br>
        <b>MIC HARDWARE:</b> READY
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("⚙ CONFIGURE GROQ KEY", expanded=(st.session_state.groq_api_key == "")):
        api_input = st.text_input("Enter Groq API Key:", value=st.session_state.groq_api_key, type="password", placeholder="gsk_...")
        if st.button("Save Key"):
            st.session_state.groq_api_key = api_input.strip()
            st.toast("✅ Groq Key saved.")
            st.rerun()

    st.session_state.voice_enabled = st.checkbox("🎙️ J.A.R.V.I.S. Voice Audio", value=st.session_state.voice_enabled)

    if st.button("🗑 CLEAR CHAT"):
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Chat log purged, sir. Systems standing by."}
        ]
        st.toast("History wiped.")
        st.rerun()

    st.markdown("---")
    st.markdown("### // SUIT KINEMATICS & MOTORS")
    st.progress(0.42, text="KNEE ACTUATORS: 41.8 Nm")
    st.progress(0.994, text="HIP STABILIZER: 99.4%")
    st.progress(0.98, text="BATTERY CORE: 98%")

# --- MAIN HUD ---
st.markdown("<h2 class='hud-header'>J.A.R.V.I.S. // MARK VII INTERFACE</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### // NEURAL AI TERMINAL")

    for msg in st.session_state.chat_history:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🦾"):
                st.write(f"**J.A.R.V.I.S.:** {msg['content']}")
        else:
            with st.chat_message("user", avatar="👤"):
                st.write(f"**Commander:** {msg['content']}")

    user_input = st.chat_input("Enter tactical command, sir...")

    st.markdown("---")
    st.markdown("### // AUTONOMOUS AGENT CREATOR")
    c1, c2, c3, c4 = st.columns(4)
    quick_prompt = None

    with c1:
        if st.button("📄 STATUS REPORT"):
            quick_prompt = "Jarvis, provide a technical diagnostic on Mark VII armor status."
    with c2:
        if st.button("📊 TACTICAL SLIDES"):
            quick_prompt = "Jarvis, draft a tactical briefing presentation for upcoming defense operations."
    with c3:
        if st.button("📝 SPECS DOC"):
            quick_prompt = "Jarvis, list suit telemetry specifications."
    with c4:
        if st.button("💥 FIRE REPULSOR"):
            quick_prompt = "Jarvis, discharge repulsor pulse at maximum yield!"

    active_prompt = user_input or quick_prompt

    if active_prompt:
        st.session_state.chat_history.append({"role": "user", "content": active_prompt})

        if st.session_state.groq_api_key:
            try:
                client = Groq(api_key=st.session_state.groq_api_key)
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.chat_history[-6:]:
                    messages.append({"role": m["role"], "content": m["content"]})

                with st.spinner("J.A.R.V.I.S. processing..."):
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model="llama-3.3-70b-versatile",
                        temperature=0.7,
                        max_tokens=300,
                    )
                    reply = chat_completion.choices[0].message.content
            except Exception as e:
                reply = f"Apologies, sir. Cognitive bridge error: {str(e)}"
        else:
            reply = f"Acknowledged, sir: '{active_prompt}'. For live cognitive AI replies, please enter your Groq API key in the sidebar."

        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state.last_reply_to_speak = reply

        if len(st.session_state.chat_history) > 30:
            st.session_state.chat_history = st.session_state.chat_history[-30:]

        st.rerun()

    if st.session_state.voice_enabled and st.session_state.last_reply_to_speak:
        play_browser_voice(st.session_state.last_reply_to_speak)
        st.session_state.last_reply_to_speak = ""

with col2:
    st.markdown("### // HARDWARE & SECURITY SHIELD")
    
    with st.expander("> SUIT SCHEMATICS (MARK VII)", expanded=True):
        st.markdown("""
        **5-Phase Engineering Roadmap:**
        1. *Chassis Fabrication:* Titanium-alloy micro-lattice.
        2. *Actuator Assembly:* CAN-Bus joint synchronization.
        3. *Core Power:* Micro Arc Reactor / Solid-state linkage.
        4. *Avionics & ROS2:* Flight stability kinematics.
        5. *Neural Interface:* Low-latency Groq LLM bridge.
        """)

    st.markdown("#### // ANTIVIRUS SHIELD")
    st.markdown("""
    <div class='status-card'>
        <b>HEURISTIC SCANNER:</b> ACTIVE<br>
        <b>FIRMWARE SHIELD:</b> v4.24-SECURE
    </div>
    """, unsafe_allow_html=True)
    
    sec_col1, sec_col2 = st.columns(2)
    with sec_col1:
        if st.button("🔍 VIRUS SCAN"):
            st.success("Bus clean. No anomalies detected.")
    with sec_col2:
        if st.button("🛡️ COUNTER-PATCH"):
            st.info("Firmware counter-patch v4.25 deployed.")

    st.markdown("#### // AUTONOMOUS SAFE-WEB AGENT")
    target_url = st.text_input("Safe sandbox URL:", placeholder="https://stark-industries.com")
    if st.button("VERIFY & OPEN SAFELY"):
        if target_url:
            with st.spinner("Analyzing target..."):
                result = sandbox_url_inspect(target_url)
            st.success(f"Result: {result}")
        else:
            st.error("Please supply a valid URL target.")
