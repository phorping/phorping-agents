import streamlit as st
import streamlit.components.v1 as components
import anthropic
import base64
import os
import requests
import json
import xml.etree.ElementTree as ET


def load_agent_system(key):
    path = f"agents/{key}.md"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def search_pubmed(query, max_results=5):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    try:
        r = requests.get(base + "esearch.fcgi", params={
            "db": "pubmed", "term": query, "retmax": max_results,
            "retmode": "json", "sort": "relevance"
        }, timeout=10)
        pmids = r.json().get("esearchresult", {}).get("idlist", [])
        if not pmids:
            return "No PubMed results found for this query."

        r2 = requests.get(base + "efetch.fcgi", params={
            "db": "pubmed", "id": ",".join(pmids),
            "retmode": "xml", "rettype": "abstract"
        }, timeout=10)

        root = ET.fromstring(r2.content)
        results = []
        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", "No title")
            abstract = article.findtext(".//AbstractText", "No abstract available")
            journal = article.findtext(".//Journal/Title", "Unknown journal")
            year = article.findtext(".//PubDate/Year", "")
            month = article.findtext(".//PubDate/Month", "")
            pub_date = f"{year} {month}".strip()

            authors = []
            for author in article.findall(".//Author")[:3]:
                last = author.findtext("LastName", "")
                if last:
                    authors.append(last)
            author_str = ", ".join(authors) + (" et al." if len(authors) >= 3 else "")

            pmid = article.findtext(".//PMID", "")
            pmc_id = None
            for aid in article.findall(".//ArticleId"):
                if aid.get("IdType") == "pmc":
                    pmc_id = aid.text
                    break

            results.append({
                "pmid": pmid,
                "title": title,
                "authors": author_str,
                "journal": journal,
                "published": pub_date,
                "abstract": abstract[:600] + "..." if len(abstract) > 600 else abstract,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "full_text_available": pmc_id is not None,
                "full_text_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/" if pmc_id else None,
            })
        return results
    except Exception as e:
        return f"PubMed search error: {str(e)}"


DEXTER_TOOLS = [
    {
        "name": "search_pubmed",
        "description": (
            "Search PubMed for peer-reviewed medical literature. "
            "Use this whenever Phorping asks about medical topics, new research, clinical guidelines, "
            "or journal updates. Returns titles, authors, journal, publication date, abstract, and URL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "PubMed search query. Use MeSH terms and boolean operators for precision."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 5, max 10)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
]


def run_dexter(client, system, history):
    messages = list(history)
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system,
            messages=messages,
            tools=DEXTER_TOOLS,
        )
        if response.stop_reason == "tool_use":
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for tu in tool_uses:
                if tu.name == "search_pubmed":
                    with st.spinner(f"🔬 Searching PubMed: {tu.input.get('query', '')}..."):
                        result = search_pubmed(tu.input["query"], tu.input.get("max_results", 5))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": json.dumps(result)
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            return "".join(b.text for b in response.content if hasattr(b, "text"))


st.set_page_config(page_title="Phorping Agents", page_icon="⚔", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #f5f0e8 !important; }
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
        "system": load_agent_system("kirby"),
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
        "system": load_agent_system("dexter"),
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
        "system": load_agent_system("typhus"),
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
        "system": load_agent_system("johnny"),
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
        "system": load_agent_system("buzz"),
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
        "system": load_agent_system("alien"),
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
        "system": load_agent_system("mojo"),
    },
    "Genie": {
        "emoji": "🧞", "color": "#4A90E2",
        "role": "Psychotherapist",
        "tagline": "Ten thousand years of listening. All yours.",
        "qualifications": [
            "Emotional support & venting",
            "Grief processing (no rush)",
            "Stress & burnout from clinical work",
            "CBT-style thought reframing",
        ],
        "system": load_agent_system("genie"),
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
    "Genie": "genie",
}

CARD_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
body{background:transparent;font-family:'Cinzel',serif;}

.title{
    text-align:center;padding:12px 0 24px;
    color:#5a3e1b;font-size:26px;font-weight:900;
    text-transform:uppercase;letter-spacing:5px;
    text-shadow:0 1px 2px rgba(90,62,27,0.2);
}

.grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:16px;padding:0 12px 16px;
}

.rg-card{perspective:1200px;cursor:pointer;height:268px;user-select:none;}

@keyframes nudge{
    0%  {transform:scale(1) rotate(0deg);}
    20% {transform:scale(1.07) rotate(-3deg);}
    40% {transform:scale(1.07) rotate(3deg);}
    60% {transform:scale(1.04) rotate(-1.5deg);}
    80% {transform:scale(1.02) rotate(1deg);}
    100%{transform:scale(1) rotate(0deg);}
}
.rg-card.nudge{animation:nudge 0.4s ease;}

.card-inner{
    width:100%;height:100%;
    position:relative;
    transform-style:preserve-3d;
    transition:transform 0.75s cubic-bezier(0.4,0.2,0.2,1);
}
.rg-card.flipped .card-inner{transform:rotateY(180deg);}

.card-face{
    position:absolute;width:100%;height:100%;
    backface-visibility:hidden;-webkit-backface-visibility:hidden;
    border-radius:10px;
    border:2px solid #b8922a;
    box-shadow:0 4px 20px rgba(90,62,27,0.15),0 1px 4px rgba(90,62,27,0.1);
    display:flex;flex-direction:column;
    align-items:center;justify-content:center;
    padding:14px;overflow:hidden;
}
.card-front{background:linear-gradient(160deg,#fffdf7,#fdf5e6);}
.card-back{
    transform:rotateY(180deg);
    background:linear-gradient(160deg,#fef9ee,#faf0d8);
    justify-content:flex-start;align-items:flex-start;padding:14px 13px;
}

.card-face::before,.card-face::after{
    content:'';position:absolute;
    width:16px;height:16px;
    border-color:#b8922a;border-style:solid;
    opacity:0.6;
}
.card-face::before{top:8px;left:8px;border-width:2px 0 0 2px;}
.card-face::after{bottom:8px;right:8px;border-width:0 2px 2px 0;}

.avatar-ring{
    width:84px;height:84px;border-radius:50%;
    border:3px solid;
    display:flex;align-items:center;justify-content:center;
    margin-bottom:10px;font-size:42px;
    overflow:hidden;position:relative;
    box-shadow:0 0 10px rgba(0,0,0,0.1);
}

/* Smooth crossfade between still and gif */
.avatar-container{position:relative;width:78px;height:78px;}
.avatar-static{
    position:absolute;top:0;left:0;
    width:78px;height:78px;object-fit:contain;border-radius:50%;
    opacity:1;transition:opacity 0.45s ease;
}
.avatar-gif{
    position:absolute;top:0;left:0;
    width:78px;height:78px;object-fit:contain;border-radius:50%;
    opacity:0;transition:opacity 0.45s ease;
}
.rg-card:hover .avatar-static{opacity:0;}
.rg-card:hover .avatar-gif{opacity:1;}

.agent-name{
    color:#2a1a0a;font-size:13px;font-weight:700;
    text-transform:uppercase;letter-spacing:2px;text-align:center;
}
.agent-role{
    color:#8b6914;font-size:8.5px;
    text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;
}
.hint{
    position:absolute;bottom:7px;left:0;right:0;
    text-align:center;color:rgba(90,62,27,0.3);
    font-size:7px;letter-spacing:1px;font-family:'Cinzel',serif;
}

.back-name{
    color:#2a1a0a;font-size:12px;font-weight:700;
    text-align:center;width:100%;
    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:4px;
}
.back-divider{
    width:100%;height:1px;
    background:linear-gradient(to right,transparent,#b8922a,transparent);
    margin:3px 0 8px;
}
.ag-tagline{
    color:#8b6914;font-size:9.5px;font-style:italic;
    text-align:center;width:100%;margin-bottom:9px;line-height:1.4;
}
.qual{
    color:#3a2a10;font-size:10px;
    padding:3.5px 0;
    border-bottom:1px solid rgba(184,146,42,0.2);
    width:100%;
}
.qual::before{content:"⚔ ";color:#b8922a;}
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
    if static:
        gif_tag = f'<img class="avatar-gif" src="{gif}">' if gif else ""
        return (
            f'<div class="avatar-container">'
            f'<img class="avatar-static" src="{static}">'
            f'{gif_tag}'
            f'</div>'
        )
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
var flippedCard = null;

function goToChat(name) {{
    var a = document.createElement('a');
    a.href = '?agent=' + encodeURIComponent(name);
    a.target = '_top';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}}

document.querySelectorAll('.rg-card').forEach(function(card) {{
    card.addEventListener('click', function() {{
        var name = this.dataset.agent;
        var el = this;

        if (timers[name]) {{
            // Double click — nudge then navigate
            clearTimeout(timers[name]);
            delete timers[name];
            el.classList.add('nudge');
            setTimeout(function() {{
                el.classList.remove('nudge');
                goToChat(name);
            }}, 420);
        }} else {{
            // Single click — wait to confirm it's not a double click
            timers[name] = setTimeout(function() {{
                delete timers[name];
                // Flip back any other open card
                if (flippedCard && flippedCard !== el) {{
                    flippedCard.classList.remove('flipped');
                }}
                // Toggle this card
                if (el.classList.contains('flipped')) {{
                    el.classList.remove('flipped');
                    flippedCard = null;
                }} else {{
                    el.classList.add('flipped');
                    flippedCard = el;
                }}
            }}, 280);
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
      <h2 style='font-family:"Cinzel",serif;color:#2a1a0a;margin:0;'>
        {agent['emoji']} &nbsp; {name}
      </h2>
      <div style='color:#8b6914;font-size:12px;font-style:italic;margin:5px 0 14px;'>
        "{agent['tagline']}"
      </div>
      <div style='height:1px;background:linear-gradient(to right,transparent,#b8922a,transparent);
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
            if name == "Dexter":
                reply = run_dexter(client, agent["system"], history)
                st.write(reply)
            else:
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
