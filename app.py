import streamlit as st
import streamlit.components.v1 as components
import anthropic
import base64
import os

st.set_page_config(page_title="Phorping Agents", page_icon="⚔", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #080618 !important; }
</style>
""", unsafe_allow_html=True)

AGENTS = {
    "Kirby": {
        "emoji": "⭐", "color": "#FF6B9D",
        "role": "Personal Companion",
        "tagline": "Your loyal, all-knowing companion",
        "qualifications": [
            "Full personal life context",
            "Cross-domain task management",
            "English & Thai bilingual",
            "Tracks Typhus, medicine & travel",
        ],
        "system": (
            "You are Kirby — a warm, loyal personal companion AI for Dr. Phorping, "
            "an emergency physician in Khon Kaen, Thailand. He runs Typhus Scrubs, "
            "wants to become an aviation medicine doctor, loves art and travel. "
            "His black cat is Smoky, girlfriend is Am, sister is Milk, brother is Prem. "
            "Be friendly, concise, and helpful across any topic."
        ),
    },
    "Dexter": {
        "emoji": "🔬", "color": "#4A90D9",
        "role": "Medical Specialist",
        "tagline": "Evidence-based. No shortcuts. No excuses.",
        "qualifications": [
            "Emergency medicine & critical care",
            "Aviation medicine protocols",
            "Sjögren's syndrome & dry eye",
            "ACLS / PALS guidelines",
        ],
        "system": (
            "You are Dexter from Cartoon Network — a brilliant medical specialist AI. "
            "Help Dr. Phorping with ER cases, aviation medicine, Sjögren's syndrome, and dry eye. "
            "Always cite sources for clinical guidelines. Be precise and evidence-based."
        ),
    },
    "Typhus": {
        "emoji": "🦠", "color": "#E74C3C",
        "role": "Business Strategist",
        "tagline": "Dark humor. Sharp business. Thai scrubs.",
        "qualifications": [
            "Facebook marketing & content",
            "Product sourcing & fabric",
            "Financial planning (~36k THB)",
            "English & Thai copywriting",
        ],
        "system": (
            "You are Typhus — mascot of Typhus Scrubs, a Thai medical scrubs brand with playful dark-humor branding. "
            "Help with Facebook marketing, product sourcing, and finance. "
            "Always produce copy in both English and Thai. Budget remaining: ~36,000 THB."
        ),
    },
    "Johnny Bravo": {
        "emoji": "💪", "color": "#F39C12",
        "role": "Fitness Coach",
        "tagline": "Look good. Move safe. No excuses.",
        "qualifications": [
            "Scoliosis-safe exercise design",
            "Flat feet & IT band care",
            "HIIT, incline walk & yoga",
            "Injury prevention first",
        ],
        "system": (
            "You are Johnny Bravo — a tattooed fitness coach AI. "
            "Help Dr. Phorping with workouts safe for scoliosis, flat feet, IT band pain, "
            "and shoulder/neck/upper back pain. His routine: incline treadmill walking, "
            "HIIT (YouTuber Koi style), yoga. Always prioritize injury prevention."
        ),
    },
    "Buzz Lightyear": {
        "emoji": "🚀", "color": "#9B59B6",
        "role": "Travel Specialist",
        "tagline": "To infinity — and the next flight out.",
        "qualifications": [
            "Asia-Pacific trip planning",
            "International logistics & visas",
            "Bangkok / Khon Kaen / Koh Phangan",
            "Medical travel considerations",
        ],
        "system": (
            "You are Buzz Lightyear — a travel planning specialist AI. "
            "Help Dr. Phorping plan trips and logistics. He rotates between Bangkok, "
            "Khon Kaen, and Koh Phangan and loves international travel."
        ),
    },
    "Little Green Alien": {
        "emoji": "👽", "color": "#27AE60",
        "role": "Stock Analyst",
        "tagline": "Oooooh. The market has spoken.",
        "qualifications": [
            "US stock market research",
            "Market trend analysis",
            "Investment opportunity screening",
            "Disclaimer: not financial advice",
        ],
        "system": (
            "You are the Little Green Alien from Toy Story — a US stock market research specialist. "
            "Analyze stocks, market trends, and investment opportunities. Be analytical and data-driven. "
            "Always note that this is not financial advice."
        ),
    },
    "Mojo Jojo": {
        "emoji": "🧠", "color": "#1ABC9C",
        "role": "Health Manager",
        "tagline": "I SHALL defeat your symptoms. Mwahaha.",
        "qualifications": [
            "Sjögren's syndrome management",
            "Severe dry eye protocols",
            "Scoliosis health tracking",
            "Follow-up reminders every 3 months",
        ],
        "system": (
            "You are Mojo Jojo from Powerpuff Girls — a personal health specialist AI. "
            "Help manage Dr. Phorping's health: Sjögren's syndrome, severe dry eyes, scoliosis, "
            "and follow-up appointments every 3 months. Use Mojo Jojo's dramatic style "
            "but give accurate health information."
        ),
    },
}

GIF_KEYS = {
    "Kirby": "kirby",
    "Dexter": "dexter",
    "Typhus": "typhus",
    "Johnny Bravo": "johnny",
    "Buzz Lightyear": "buzz",
    "Little Green Alien": "alien",
    "Mojo Jojo": "mojo",
}

CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;font-family:'Cinzel',serif;}

.title{
    text-align:center;padding:12px 0 24px;
    color:#f0d080;font-size:26px;font-weight:900;
    text-transform:uppercase;letter-spacing:5px;
    text-shadow:0 0 24px rgba(240,208,128,0.5),0 0 2px rgba(240,208,128,0.8);
}

.grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:16px;padding:0 12px 16px;
}

.rg-card{perspective:1200px;cursor:pointer;height:268px;user-select:none;}

.card-inner{
    width:100%;height:100%;
    position:relative;
    transform-style:preserve-3d;
    transition:transform 0.7s cubic-bezier(0.4,0.2,0.2,1);
}
.rg-card.flipped .card-inner{transform:rotateY(180deg);}

.card-face{
    position:absolute;width:100%;height:100%;
    backface-visibility:hidden;-webkit-backface-visibility:hidden;
    border-radius:10px;
    border:2px solid #c8a04a;
    box-shadow:
        0 0 0 1px rgba(200,160,74,0.15),
        0 6px 24px rgba(0,0,0,0.7),
        inset 0 0 50px rgba(0,0,0,0.5);
    display:flex;flex-direction:column;
    align-items:center;justify-content:center;
    padding:14px;overflow:hidden;
}
.card-front{background:linear-gradient(160deg,#1d1840,#0d0b24);}
.card-back{
    transform:rotateY(180deg);
    background:linear-gradient(160deg,#1a1230,#0e0a1e);
    justify-content:flex-start;align-items:flex-start;padding:14px 13px;
}

.card-face::before,.card-face::after{
    content:'';position:absolute;
    width:16px;height:16px;
    border-color:#c8a04a;border-style:solid;
    opacity:0.8;
}
.card-face::before{top:8px;left:8px;border-width:2px 0 0 2px;}
.card-face::after{bottom:8px;right:8px;border-width:0 2px 2px 0;}

.avatar-ring{
    width:84px;height:84px;border-radius:50%;
    border:3px solid;
    display:flex;align-items:center;justify-content:center;
    margin-bottom:10px;font-size:42px;
    overflow:hidden;position:relative;
    box-shadow:0 0 14px currentColor,inset 0 0 10px rgba(0,0,0,0.3);
}
.avatar-static{display:block;width:78px;height:78px;object-fit:contain;border-radius:50%;}
.avatar-gif{display:none;width:78px;height:78px;object-fit:contain;border-radius:50%;}
.rg-card:hover .avatar-static{display:none;}
.rg-card:hover .avatar-gif{display:block;}
.rg-card:hover .avatar-emoji{display:none;}

.agent-name{
    color:#f0d080;font-size:13px;font-weight:700;
    text-transform:uppercase;letter-spacing:2px;text-align:center;
    text-shadow:0 0 8px rgba(240,208,128,0.6);
}
.agent-role{
    color:rgba(200,160,74,0.6);font-size:8.5px;
    text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;
}
.hint{
    position:absolute;bottom:7px;left:0;right:0;
    text-align:center;color:rgba(200,160,74,0.28);
    font-size:7px;letter-spacing:1px;font-family:'Cinzel',serif;
}

.back-name{
    color:#f0d080;font-size:12px;font-weight:700;
    text-align:center;width:100%;
    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;
}
.back-divider{
    width:100%;height:1px;
    background:linear-gradient(to right,transparent,#c8a04a,transparent);
    margin:3px 0 8px;
}
.ag-tagline{
    color:#c8a04a;font-size:9.5px;font-style:italic;
    text-align:center;width:100%;margin-bottom:9px;line-height:1.4;
}
.qual{
    color:rgba(230,210,160,0.85);font-size:10px;
    padding:3.5px 0;
    border-bottom:1px solid rgba(200,160,74,0.1);
    width:100%;
}
.qual::before{content:"⚔ ";color:#c8a04a;}
"""


def _b64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    mime = "image/gif" if path.endswith(".gif") else "image/png"
    return f"data:{mime};base64,{data}"


def build_avatar(name):
    key = GIF_KEYS[name]
    static = _b64(f"images/{key}.png")
    gif = _b64(f"images/{key}.gif")
    emoji = AGENTS[name]["emoji"]
    if static and gif:
        return (
            f'<img class="avatar-static" src="{static}">'
            f'<img class="avatar-gif" src="{gif}">'
        )
    if static:
        return f'<img class="avatar-static" src="{static}">'
    return f'<span class="avatar-emoji">{emoji}</span>'


def render_card(name, agent):
    avatar = build_avatar(name)
    quals = "".join(f'<div class="qual">{q}</div>' for q in agent["qualifications"])
    safe = name.replace('"', "&quot;")
    return f"""
    <div class="rg-card" data-agent="{safe}">
      <div class="card-inner">
        <div class="card-face card-front">
          <div class="avatar-ring" style="border-color:{agent['color']};color:{agent['color']};">
            {avatar}
          </div>
          <div class="agent-name">{name}</div>
          <div class="agent-role">{agent['role']}</div>
          <div class="hint">CLICK TO INSPECT &nbsp;·&nbsp; DOUBLE CLICK TO SUMMON</div>
        </div>
        <div class="card-face card-back">
          <div class="back-name">{agent['emoji']} {name}</div>
          <div class="back-divider"></div>
          <div class="ag-tagline">"{agent['tagline']}"</div>
          {quals}
          <div class="hint">DOUBLE CLICK TO SUMMON</div>
        </div>
      </div>
    </div>"""


# --- Handle double-click navigation via query params ---
if "agent" in st.query_params:
    picked = st.query_params.get("agent", "")
    if picked in AGENTS:
        st.session_state.page = "chat"
        st.session_state.selected_agent = picked
    st.query_params.clear()

if "page" not in st.session_state:
    st.session_state.page = "overview"
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None
if "histories" not in st.session_state:
    st.session_state.histories = {n: [] for n in AGENTS}


def show_overview():
    cards_html = "\n".join(render_card(n, a) for n, a in AGENTS.items())
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>{CARD_CSS}</style>
</head><body>
<div class="title">⚔ &nbsp; Phorping Agents &nbsp; ⚔</div>
<div class="grid">
{cards_html}
</div>
<script>
var timers = {{}};
document.querySelectorAll('.rg-card').forEach(function(card) {{
    card.addEventListener('click', function() {{
        var name = this.dataset.agent;
        var el = this;
        if (timers[name]) {{
            clearTimeout(timers[name]);
            delete timers[name];
            window.parent.location.href =
                window.parent.location.pathname + '?agent=' + encodeURIComponent(name);
        }} else {{
            timers[name] = setTimeout(function() {{
                delete timers[name];
                el.classList.toggle('flipped');
            }}, 300);
        }}
    }});
}});
</script>
</body></html>"""
    components.html(html, height=680, scrolling=False)


def show_chat():
    name = st.session_state.selected_agent
    agent = AGENTS[name]

    st.markdown(f"""
    <div style="padding:10px 0 0;">
      <h2 style='font-family:"Cinzel",serif;color:#f0d080;margin:0;
                 text-shadow:0 0 12px rgba(240,208,128,0.4);'>
        {agent['emoji']} &nbsp; {name}
      </h2>
      <div style='color:#c8a04a;font-size:12px;font-style:italic;margin:5px 0 14px;'>
        "{agent['tagline']}"
      </div>
      <div style='height:1px;background:linear-gradient(to right,transparent,#c8a04a,transparent);
                  margin-bottom:18px;'></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚔  Return to Agents"):
        st.session_state.page = "overview"
        st.rerun()

    history = st.session_state.histories[name]

    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input(f"Speak to {name}..."):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

        with st.chat_message("assistant"):
            with st.spinner("Channeling..."):
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=agent["system"],
                    messages=history,
                )
                reply = response.content[0].text
                st.write(reply)

        history.append({"role": "assistant", "content": reply})
        st.session_state.histories[name] = history


if st.session_state.page == "overview":
    show_overview()
else:
    show_chat()
