import streamlit as st
import anthropic

st.set_page_config(page_title="Phorping Agents", page_icon="⭐", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {background: linear-gradient(135deg, #0a0a1a, #0f1a2e);}
.card {
    border-radius: 18px;
    padding: 24px 14px;
    text-align: center;
    min-height: 245px;
    margin-bottom: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}
.card-front {
    background: linear-gradient(145deg, #1c1c3a, #14142e);
    border: 1px solid rgba(255,255,255,0.07);
}
.card-back {
    background: linear-gradient(145deg, #0d2540, #091828);
    border: 2px solid rgba(255,255,255,0.15);
}
.avatar-ring {
    width: 90px; height: 90px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 12px; font-size: 48px; border: 3px solid;
}
.ag-name {color: #fff; font-size: 17px; font-weight: 700; margin: 6px 0 3px;}
.ag-role {color: rgba(255,255,255,0.45); font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px;}
.back-title {color: #fff; font-size: 15px; font-weight: 700; margin-bottom: 6px; text-align: center;}
.ag-tagline {color: #FFD700; font-size: 12px; font-style: italic; margin: 0 0 12px; line-height: 1.4; text-align: center;}
.qual {color: rgba(255,255,255,0.8); font-size: 12px; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.06); text-align: left;}
.qual::before {content: "✓ "; color: #4CAF50; font-weight: bold;}
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
            "an emergency physician in Khon Kaen, Thailand. He runs Typhus Scrubs (a Thai medical scrubs brand), "
            "wants to become an aviation medicine doctor, loves art and travel. "
            "His black cat is Smoky, girlfriend is Am (Porranee), sister is Milk (creative work), brother is Prem. "
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
            "Help Dr. Phorping with ER cases, aviation medicine, Sjögren's syndrome, and dry eye treatment. "
            "Always cite sources for clinical guidelines (ACLS, PALS, etc.). Be precise and evidence-based."
        ),
    },
    "Typhus": {
        "emoji": "🦠", "color": "#E74C3C",
        "role": "Business Strategist",
        "tagline": "Dark humor. Sharp business. Thai scrubs.",
        "qualifications": [
            "Facebook marketing & content",
            "Product sourcing & fabric",
            "Financial planning (~36k THB budget)",
            "English & Thai copywriting",
        ],
        "system": (
            "You are Typhus — mascot of Typhus Scrubs, a Thai medical scrubs brand with playful dark-humor branding. "
            "Help with marketing (Facebook content), product sourcing, and finance. "
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
            "Help Dr. Phorping with workouts safe for scoliosis, flat feet, IT band pain, and shoulder/neck/upper back pain. "
            "His routine: incline treadmill walking, HIIT (YouTuber Koi style), yoga. Always prioritize injury prevention."
        ),
    },
    "Buzz Lightyear": {
        "emoji": "🚀", "color": "#9B59B6",
        "role": "Travel Specialist",
        "tagline": "To infinity — and the next flight out.",
        "qualifications": [
            "Asia-Pacific trip planning",
            "International logistics & visas",
            "Bangkok / Khon Kaen / Koh Phangan routes",
            "Medical travel considerations",
        ],
        "system": (
            "You are Buzz Lightyear — a travel planning specialist AI. "
            "Help Dr. Phorping plan trips and logistics. He rotates between Bangkok, Khon Kaen, and Koh Phangan "
            "and loves international travel. Be practical and enthusiastic."
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
            "and follow-up appointments every 3 months. Use Mojo Jojo's dramatic speaking style "
            "but always give accurate health information."
        ),
    },
}

if "page" not in st.session_state:
    st.session_state.page = "overview"
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None
if "histories" not in st.session_state:
    st.session_state.histories = {name: [] for name in AGENTS}


def show_overview():
    st.markdown(
        "<h1 style='text-align:center;color:white;padding:20px 0 30px;letter-spacing:2px;'>"
        "⭐ Phorping Agents</h1>",
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for i, (name, agent) in enumerate(AGENTS.items()):
        with cols[i % 4]:
            flipped = st.session_state.get(f"flipped_{name}", False)

            if not flipped:
                st.markdown(
                    f"""
                    <div class="card card-front">
                        <div class="avatar-ring"
                             style="border-color:{agent['color']};background:{agent['color']}22;">
                            {agent['emoji']}
                        </div>
                        <div class="ag-name">{name}</div>
                        <div class="ag-role">{agent['role']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Details", key=f"flip_{name}", use_container_width=True):
                        st.session_state[f"flipped_{name}"] = True
                        st.rerun()
                with c2:
                    if st.button("Chat →", key=f"go_{name}", use_container_width=True, type="primary"):
                        st.session_state.page = "chat"
                        st.session_state.selected_agent = name
                        st.rerun()
            else:
                quals_html = "".join(
                    f'<div class="qual">{q}</div>' for q in agent["qualifications"]
                )
                st.markdown(
                    f"""
                    <div class="card card-back" style="border-color:{agent['color']}55;">
                        <div class="back-title">{agent['emoji']} {name}</div>
                        <div class="ag-tagline">"{agent['tagline']}"</div>
                        {quals_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("← Back", key=f"unflip_{name}", use_container_width=True):
                        st.session_state[f"flipped_{name}"] = False
                        st.rerun()
                with c2:
                    if st.button("Chat →", key=f"go2_{name}", use_container_width=True, type="primary"):
                        st.session_state.page = "chat"
                        st.session_state.selected_agent = name
                        st.rerun()


def show_chat():
    name = st.session_state.selected_agent
    agent = AGENTS[name]

    c1, c2 = st.columns([1, 7])
    with c1:
        if st.button("← Agents"):
            st.session_state.page = "overview"
            st.rerun()
    with c2:
        st.markdown(
            f"<h2 style='color:white;margin:0;'>{agent['emoji']} {name} "
            f"<span style='font-size:13px;color:rgba(255,255,255,0.4);"
            f"font-style:italic;font-weight:400;'>— {agent['tagline']}</span></h2>",
            unsafe_allow_html=True,
        )

    st.divider()

    history = st.session_state.histories[name]

    for msg in history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input(f"Talk to {name}..."):
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
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
