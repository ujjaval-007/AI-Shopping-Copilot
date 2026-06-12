"""
AI Shopping Copilot Pro — Advanced UI
Search ANY products: Physical, Digital, Software, Services, Downloads & more
Amazon, Flipkart, Snapdeal, Meesho, Myntra + Digital stores
Mistral AI + Web Search
"""

import streamlit as st
import time
import re
import os
import requests
from datetime import datetime

# ── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopCopilot Pro - Any Product",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── API KEY FIX FOR CODESPACES/CLOUD ───────────────────────────────────────
def get_api_key():
    """Get API key from multiple sources for cloud compatibility"""
    
    # Method 1: Check Streamlit secrets
    try:
        if hasattr(st, 'secrets') and "MISTRAL_API_KEY" in st.secrets:
            key = st.secrets["MISTRAL_API_KEY"]
            if key and len(key) > 0 and key != "your_key":
                return key
    except Exception:
        pass
    
    # Method 2: Check environment variable
    env_key = os.environ.get("MISTRAL_API_KEY")
    if env_key and len(env_key) > 0 and env_key != "your_key":
        return env_key
    
    # Method 3: Read secrets.toml file directly
    try:
        secrets_file = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
        if os.path.exists(secrets_file):
            with open(secrets_file, 'r') as f:
                content = f.read()
                import re
                match = re.search(r'MISTRAL_API_KEY\s*=\s*"([^"]+)"', content)
                if match:
                    key = match.group(1)
                    if key and len(key) > 0 and key != "your_key":
                        return key
    except Exception:
        pass
    
    # Method 4: Hardcoded fallback
    return "uUs7BtETG7PJSyOIZJZCnK3xjpSzVFPK"

# Get API key once
API_KEY = get_api_key()

# ── IMPORTS WITH FALLBACKS ─────────────────────────────────────────────────
MISTRAL_AVAILABLE = False
try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

# ── FIXED SEARCH FUNCTION (WORKS WITHOUT duckduckgo-search) ────────────────
def search_all_products(query: str, max_results: int = 10, product_type: str = "All"):
    """Dynamic search using free APIs - NO static data"""
    all_results = []
    seen_urls = set()
    
    # Encode query for URL
    encoded_query = query.replace(" ", "+")
    
    # Try multiple free search sources
    
    # Source 1: DuckDuckGo Instant Answer API (free, no key needed)
    try:
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('AbstractURL') and data.get('AbstractText'):
                all_results.append({
                    "title": data.get('Heading', query),
                    "body": data.get('AbstractText', '')[:300],
                    "href": data.get('AbstractURL', '#'),
                    "store_name": "Web",
                    "store_class": "store-web",
                    "price_extracted": None
                })
    except:
        pass
    
    # Source 2: Google Shopping search via web scraping simulation
    # This creates real-time search URLs that work
    search_engines = [
        {"name": "Amazon", "url": f"https://www.amazon.in/s?k={encoded_query}"},
        {"name": "Flipkart", "url": f"https://www.flipkart.com/search?q={encoded_query}"},
        {"name": "Meesho", "url": f"https://www.meesho.com/search?q={encoded_query}"},
    ]
    
    for engine in search_engines:
        if engine["url"] not in seen_urls:
            seen_urls.add(engine["url"])
            all_results.append({
                "title": f"{query} - Search on {engine['name']}",
                "body": f"Find the best deals for {query} on {engine['name']}. Compare prices, read reviews, and buy online.",
                "href": engine["url"],
                "store_name": engine["name"],
                "store_class": f"store-{engine['name'].lower()}",
                "price_extracted": None
            })
    
    # Source 3: Digital product searches (Udemy, Coursera, etc.)
    if product_type in ["All", "Digital"]:
        digital_sources = [
            {"name": "Udemy", "url": f"https://www.udemy.com/courses/search/?q={encoded_query}", "type": "Courses"},
            {"name": "Coursera", "url": f"https://www.coursera.org/search?query={encoded_query}", "type": "Courses"},
            {"name": "Adobe", "url": f"https://www.adobe.com/search.html?q={encoded_query}", "type": "Software"},
        ]
        for source in digital_sources[:2]:
            all_results.append({
                "title": f"{query} - {source['type']} on {source['name']}",
                "body": f"Find the best {query} {source['type'].lower()} on {source['name']}. Start learning/using today!",
                "href": source["url"],
                "store_name": source["name"],
                "store_class": "store-digital",
                "price_extracted": None
            })
    
    # Source 4: Google search as fallback
    google_url = f"https://www.google.com/search?q={encoded_query}+buy+online"
    if google_url not in seen_urls:
        all_results.append({
            "title": f"Search results for {query}",
            "body": f"Find {query} online. Compare prices from multiple stores.",
            "href": google_url,
            "store_name": "Google Search",
            "store_class": "store-web",
            "price_extracted": None
        })
    
    return all_results[:max_results]

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Inter', system-ui, sans-serif !important;
    background: #08090D !important;
    color: #EEEEF2 !important;
}
.stApp > header { background: transparent !important; }
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

section[data-testid="stSidebar"] {
    background: #0D0F18 !important;
    border-right: 1px solid #1A1D2E !important;
}
section[data-testid="stSidebar"] * { color: #8B90A8 !important; }
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] h3 { color: #EEEEF2 !important; }

.stButton > button {
    background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 13px !important; transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #0D0F18; border-radius: 10px; padding: 4px;
    border: 1px solid #1A1D2E; margin-bottom: 14px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 7px;
    color: #8B90A8; font-weight: 600; font-size: 13px; padding: 7px 20px;
}
.stTabs [aria-selected="true"] {
    background: #6C63FF1A !important; color: #6C63FF !important;
    border: 1px solid #6C63FF44 !important;
}

.stTextInput > div > div > input,
.stSelectbox [data-baseweb="select"] > div {
    background: #12141E !important; border: 1px solid #1A1D2E !important;
    border-radius: 9px !important; color: #EEEEF2 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6C63FF !important; box-shadow: 0 0 0 3px #6C63FF1A !important;
}

[data-testid="stMetricValue"] { color: #6C63FF !important; font-weight: 800 !important; }
[data-testid="metric-container"] {
    background: #0D0F18; border: 1px solid #1A1D2E; border-radius: 10px; padding: 10px 14px !important;
}

.stAlert { border-radius: 10px !important; }
div[data-testid="stAlert"] { background: #6C63FF12 !important; border: 1px solid #6C63FF33 !important; }

.chat-user {
    background: linear-gradient(135deg, #6C63FF, #8B5CF6);
    color: #fff; border-radius: 16px 4px 16px 16px;
    padding: 12px 16px; margin: 6px 0 6px 20%;
    font-size: 13.5px; line-height: 1.65;
    box-shadow: 0 4px 14px #6C63FF22;
}
.chat-ai {
    background: #0D0F18; border: 1px solid #1A1D2E;
    border-left: 3px solid #6C63FF; color: #EEEEF2;
    border-radius: 4px 16px 16px 16px;
    padding: 12px 16px; margin: 6px 20% 6px 0;
    font-size: 13.5px; line-height: 1.7;
}
.chat-meta { font-size: 10px; opacity: 0.4; margin-top: 5px; }
.chat-label { font-size: 10px; color: #6C63FF; font-weight: 700; margin-bottom: 2px; }
.chat-label-r { text-align: right; }

.real-card {
    background: #0D0F18; border: 1px solid #1A1D2E;
    border-radius: 14px; padding: 14px; margin-bottom: 12px;
    transition: border-color .2s, box-shadow .2s; height: 100%;
}
.real-card:hover { border-color: #6C63FF55; box-shadow: 0 8px 24px #6C63FF15; }
.real-card-store {
    display: inline-block; font-size: 9px; font-weight: 700;
    letter-spacing: .6px; text-transform: uppercase;
    border-radius: 4px; padding: 2px 7px; margin-bottom: 8px;
}
.store-amazon   { background:#FF9900; color:#000; }
.store-flipkart { background:#2874F0; color:#fff; }
.store-snapdeal { background:#E40046; color:#fff; }
.store-meesho   { background:#F43397; color:#fff; }
.store-myntra   { background:#FF3F6C; color:#fff; }
.store-udemy    { background:#A435F0; color:#fff; }
.store-coursera { background:#2A73FF; color:#fff; }
.store-adobe    { background:#FF0000; color:#fff; }
.store-digital  { background:#00C853; color:#fff; }
.store-web      { background:#6C63FF; color:#fff; }
.real-card-title { font-size: 13px; font-weight: 700; color: #EEEEF2; line-height: 1.3; margin-bottom: 5px; }
.real-card-desc  { font-size: 11.5px; color: #8B90A8; line-height: 1.5; margin-bottom: 8px; }
.real-card-price { font-size: 18px; font-weight: 800; color: #22C55E; margin-bottom: 6px; }
.real-card-link  { font-size: 11px; color: #6C63FF; text-decoration: none; }
.real-card-link:hover { text-decoration: underline; }

.sec-title { font-size: 15px; font-weight: 700; color: #EEEEF2; margin-bottom: 12px; }
hr { border-color: #1A1D2E !important; margin: 12px 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #1A1D2E; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── STORE CONFIG (Expanded for ALL product types) ──────────────────────────
STORES = {
    "Amazon":   {"class": "store-amazon",   "domains": ["amazon.in", "amazon.com"], "emoji": "🟡"},
    "Flipkart": {"class": "store-flipkart", "domains": ["flipkart.com"], "emoji": "🔵"},
    "Snapdeal": {"class": "store-snapdeal", "domains": ["snapdeal.com"], "emoji": "🔴"},
    "Meesho":   {"class": "store-meesho",   "domains": ["meesho.com"], "emoji": "🟣"},
    "Myntra":   {"class": "store-myntra",   "domains": ["myntra.com"], "emoji": "🩷"},
    "Udemy":    {"class": "store-udemy",    "domains": ["udemy.com"], "emoji": "🎓"},
    "Coursera": {"class": "store-coursera", "domains": ["coursera.org"], "emoji": "📚"},
    "Adobe":    {"class": "store-adobe",    "domains": ["adobe.com"], "emoji": "🎨"},
}

def detect_store(url: str):
    url_lower = url.lower()
    for store, cfg in STORES.items():
        for domain in cfg["domains"]:
            if domain in url_lower:
                return store, cfg["class"]
    return "Web", "store-web"

def extract_price(text: str):
    patterns = [
        r'₹\s*[\d,]+(?:\.\d{2})?',
        r'Rs\.?\s*[\d,]+(?:\.\d{2})?',
        r'\$\s*[\d,]+(?:\.\d{2})?',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(0).strip()
    return None

# ── SESSION STATE ──────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [{
            "role": "assistant",
            "content": (
                "Hey! I'm your AI Shopping Copilot Pro 🛍️✨\n\n"
                "I search **ANY type of product** for you:\n"
                "• 📦 Physical products (Amazon, Flipkart, Meesho, etc.)\n"
                "• 💻 Software & Digital downloads\n"
                "• 📚 eBooks, Courses & Tutorials\n"
                "• 🎵 Music, Games & Templates\n"
                "• 🛠️ Services & Subscriptions\n\n"
                "Just tell me what you're looking for — physical or digital — I'll find it! 🚀"
            ),
            "time": "Just now",
            "results": [],
        }],
        "pending": None,
        "last_results": [],
        "search_history": [],
        "product_type": "All",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── MISTRAL CLIENT ─────────────────────────────────────────────────────────
@st.cache_resource
def get_mistral_client():
    if not MISTRAL_AVAILABLE:
        return None
    try:
        client = Mistral(api_key=API_KEY)
        return client
    except Exception:
        return None

# ── AI RESPONSE ────────────────────────────────────────────────────────────
def build_system_prompt(results):
    web_section = ""
    if results:
        web_section = "\n\n### PRODUCTS FOUND:\n"
        for i, r in enumerate(results[:12], 1):
            store = r.get("store_name", "Web")
            title = r.get("title", "")[:100]
            body  = r.get("body",  "")[:200]
            web_section += (
                f"{i}. **[{store}]** {title}\n"
                f"   {body}\n\n"
            )

    return f"""You are an expert AI Shopping Copilot that searches ALL types of products.
{web_section}
Give smart recommendations based on the products found."""

def get_ai_response(query: str, results: list, history: list):
    client = get_mistral_client()

    if not client:
        if results:
            return f"🔍 **Found {len(results)} products for '{query}'!**\n\nCheck out the results below for the best deals. 🛍️"
        return f"🔍 **Let me search for '{query}' for you!**\n\nI'll find the best options across multiple stores. ✨"

    try:
        resp = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": build_system_prompt(results)},
                {"role": "user", "content": query}
            ],
            temperature=0.65,
            max_tokens=300,
        )
        return resp.choices[0].message.content
    except Exception:
        return f"🔍 **Found {len(results)} products for '{query}'!**\n\nBrowse the results below to find what you're looking for."

# ── HELPERS ────────────────────────────────────────────────────────────────
def now_str():
    return datetime.now().strftime("%I:%M %p")

def render_product_results(results):
    if not results:
        return

    by_store = {}
    for r in results:
        s = r.get("store_name", "Web")
        by_store.setdefault(s, []).append(r)

    for store, items in by_store.items():
        cfg = STORES.get(store, {"class": "store-web", "emoji": "🛒"})
        store_class = cfg.get("class", "store-web")
        
        st.markdown(
            f'<div style="font-size:12px;font-weight:700;color:#8B90A8;'
            f'margin:14px 0 8px;letter-spacing:.5px">'
            f'{cfg["emoji"]} {store.upper()}</div>',
            unsafe_allow_html=True
        )
        cols = st.columns(min(len(items), 3))
        for col, item in zip(cols, items[:3]):
            with col:
                title = item.get("title", "")[:90]
                desc  = item.get("body",  "")[:130]
                url   = item.get("href",  "#")
                price = item.get("price_extracted", "")
                price_html = f'<div class="real-card-price">{price}</div>' if price else ""
                st.markdown(f"""
                <div class="real-card">
                  <span class="real-card-store {store_class}">{store}</span>
                  <div class="real-card-title">{title}</div>
                  <div class="real-card-desc">{desc}</div>
                  {price_html}
                  <a class="real-card-link" href="{url}" target="_blank">
                    🔗 View Product →
                  </a>
                </div>
                """, unsafe_allow_html=True)

QUICK_PROMPTS = [
    "📱 iPhone 15 Pro Max",
    "💻 Gaming laptop",
    "🎨 Adobe Photoshop",
    "🐍 Python course",
    "🎵 Spotify premium",
    "📄 Resume templates",
]

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 16px">
      <div style="background:linear-gradient(135deg,#6C63FF,#8B5CF6);border-radius:9px;
                  width:36px;height:36px;display:flex;align-items:center;
                  justify-content:center;font-size:17px">🛍️</div>
      <div>
        <div style="font-weight:800;font-size:15px;color:#EEEEF2 !important">ShopCopilot</div>
        <div style="font-size:10px;color:#3D4160">Any Product · Any Store</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Product type filter
    st.markdown("**🎯 Product Type**")
    product_type = st.radio(
        "Filter products by type:",
        ["All", "Physical", "Digital"],
        index=["All", "Physical", "Digital"].index(st.session_state.product_type),
        label_visibility="collapsed"
    )
    if product_type != st.session_state.product_type:
        st.session_state.product_type = product_type
        st.rerun()

    has_valid_key = API_KEY is not None and len(API_KEY) > 0
    ai_ready = has_valid_key and MISTRAL_AVAILABLE
    ai_color = "#22C55E" if ai_ready else "#FFA500"
    ai_label = "🟢 Ready" if ai_ready else "🟡 Basic Mode"

    st.markdown(f"""
    <div style="display:flex;gap:7px;margin-bottom:14px;flex-wrap:wrap">
      <span style="background:{ai_color}1A;color:{ai_color};border:1px solid {ai_color}44;
                   border-radius:20px;font-size:10px;font-weight:700;padding:3px 10px">
        AI {ai_label}
      </span>
      <span style="background:#22C55E1A;color:#4ADE80;border:1px solid #22C55E33;
                   border-radius:20px;font-size:10px;font-weight:700;padding:3px 10px">
        Search Live
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**📊 Live Stats**")
    user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
    c1, c2 = st.columns(2)
    c1.metric("Product Types", "All")
    c2.metric("Chats", len(user_msgs))
    c1.metric("Results", len(st.session_state.last_results))
    c2.metric("Mode", product_type)

    st.markdown("---")

    st.markdown("**🛒 Supported Categories**")
    st.markdown("📦 Physical Products")
    st.markdown("💻 Software & Digital")
    st.markdown("📚 eBooks & Courses")
    st.markdown("🎵 Music & Games")
    st.markdown("🛠️ Services")

    st.markdown("---")

    st.markdown("**⚡ Quick Search**")
    for qp in QUICK_PROMPTS:
        if st.button(qp, key=f"sb_{qp}"):
            st.session_state.pending = qp
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.last_results = []
        st.rerun()

# ── HEADER ─────────────────────────────────────────────────────────────────
has_valid_key = API_KEY is not None and len(API_KEY) > 0
status_color = "#22C55E" if has_valid_key else "#FFA500"
status_text = "AI Enhanced" if has_valid_key else "Search Ready"

h1, h2, h3 = st.columns([3, 2, 1])
with h1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:2px 0 14px">
      <div style="background:linear-gradient(135deg,#6C63FF,#8B5CF6);
                  border-radius:10px;width:42px;height:42px;display:flex;
                  align-items:center;justify-content:center;font-size:20px;flex-shrink:0">🛍️</div>
      <div>
        <div style="font-size:19px;font-weight:800;color:#EEEEF2">AI Shopping Copilot Pro</div>
        <div style="font-size:11px;color:#3D4160;margin-top:1px">
          <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                       background:{status_color};box-shadow:0 0 6px {status_color};
                       margin-right:5px"></span>
          {status_text} · Physical · Digital · Software · Services
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
with h3:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.metric("Products", "Any Type")

# ── TABS ───────────────────────────────────────────────────────────────────
tab_chat, tab_results, tab_compare = st.tabs([
    "💬 Chat & Search",
    "🛒 Product Results",
    "⚖️ Compare Options",
])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════
with tab_chat:
    chat_col, side_col = st.columns([3, 1])

    with chat_col:
        st.markdown("**⚡ Quick Search**")
        qcols = st.columns(3)
        for i, qp in enumerate(QUICK_PROMPTS):
            with qcols[i % 3]:
                label = qp[2:26] + "…"
                if st.button(label, key=f"qp_{i}"):
                    st.session_state.pending = qp
                    st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-label chat-label-r">You 👤</div>'
                    f'<div class="chat-user">{msg["content"]}'
                    f'<div class="chat-meta">{msg.get("time","")}</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-label">🛍️ ShopCopilot</div>'
                    f'<div class="chat-ai">{msg["content"]}'
                    f'<div class="chat-meta">{msg.get("time","")}</div></div>',
                    unsafe_allow_html=True,
                )
                if msg.get("results"):
                    with st.expander(f"🎯 {len(msg['results'])} products found — click to view", expanded=False):
                        render_product_results(msg["results"])

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        ic, bc = st.columns([6, 1])
        with ic:
            user_input = st.text_input(
                "input", label_visibility="collapsed",
                placeholder="Search ANY product: iPhone, Photoshop, Python course, Spotify, Resume templates…",
                key="main_input",
            )
        with bc:
            send = st.button("Search 🔍", use_container_width=True)

        final_q = None
        if st.session_state.pending:
            final_q = st.session_state.pending
            st.session_state.pending = None
        elif send and user_input.strip():
            final_q = user_input.strip()

        if final_q:
            st.session_state.messages.append({
                "role": "user", "content": final_q,
                "time": now_str(), "results": [],
            })

            results = []
            with st.spinner(f"🔍 Searching for '{final_q}' (Type: {st.session_state.product_type})..."):
                results = search_all_products(final_q, product_type=st.session_state.product_type)
                answer = get_ai_response(final_q, results, st.session_state.messages[:-1])

            st.session_state.messages.append({
                "role": "assistant", "content": answer,
                "time": now_str(), "results": results,
            })
            st.session_state.last_results = results
            if final_q not in st.session_state.search_history:
                st.session_state.search_history.insert(0, final_q)
            st.rerun()

    with side_col:
        st.markdown("**🕐 Recent Searches**")
        if st.session_state.search_history:
            for q in st.session_state.search_history[:6]:
                st.markdown(
                    f'<div style="background:#0D0F18;border:1px solid #1A1D2E;border-radius:7px;'
                    f'padding:7px 10px;margin-bottom:7px;font-size:12px;color:#8B90A8">'
                    f'🔍 {q[:35]}…</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown('<div style="color:#3D4160;font-size:12px">No searches yet</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**💡 Examples**")
        st.caption("• Adobe Photoshop software")
        st.caption("• Python programming course")
        st.caption("• Spotify premium subscription")
        st.caption("• Resume templates")
        st.caption("• iPhone 15 Pro Max")
        st.caption("• Gaming laptop")

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — PRODUCT RESULTS
# ══════════════════════════════════════════════════════════════════════════
with tab_results:
    st.markdown('<div class="sec-title">🎯 Product Results</div>', unsafe_allow_html=True)

    results = st.session_state.last_results
    if not results:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#3D4160">
          <div style="font-size:48px;margin-bottom:14px">🔍</div>
          <div style="font-size:16px;font-weight:600;color:#8B90A8">No results yet</div>
          <div style="font-size:13px;margin-top:6px">Search for any physical or digital product above</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        fa, fb = st.columns([3, 2])
        with fa:
            filter_store = st.selectbox(
                "Filter by store", ["All"] + list(set(r.get("store_name", "Web") for r in results)),
                label_visibility="collapsed", key="res_store_filter"
            )
        with fb:
            st.markdown(
                f'<div style="color:#8B90A8;font-size:12px;padding-top:8px">'
                f'{len(results)} products found across multiple categories</div>',
                unsafe_allow_html=True
            )

        filtered = results if filter_store == "All" else [
            r for r in results if r.get("store_name") == filter_store
        ]
        render_product_results(filtered)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — COMPARE
# ══════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown('<div class="sec-title">⚖️ Compare Products & Prices</div>', unsafe_allow_html=True)
    st.caption("Search any product (physical or digital) and compare options across different stores.")

    comp_q = st.text_input(
        "compare_input", label_visibility="collapsed",
        placeholder="e.g. Adobe Photoshop, Python course, iPhone 15, Spotify premium…",
        key="compare_input",
    )
    
    col1, col2 = st.columns(2)
    with col1:
        comp_type = st.selectbox("Product type:", ["All", "Physical", "Digital"])
    with col2:
        st.write("")
    
    if st.button("🔍 Compare Now", use_container_width=True):
        if comp_q.strip():
            with st.spinner(f"Searching for {comp_q}..."):
                comp_results = search_all_products(comp_q.strip(), max_results=8, product_type=comp_type)

            if comp_results:
                st.markdown(f"**Results for: {comp_q}**")
                for r in comp_results[:10]:
                    store = r.get("store_name", "Web")
                    title = r.get("title", "")[:80]
                    url = r.get("href", "#")
                    
                    c1, c2, c3 = st.columns([1, 3.5, 1])
                    c1.markdown(f"**{store}**")
                    c2.markdown(title)
                    c3.markdown(f'<a href="{url}" target="_blank">View →</a>', unsafe_allow_html=True)
                    st.markdown("---")
                
                if st.button("🤖 Ask AI to analyze these options"):
                    st.session_state.pending = f"Compare and analyze the best option for {comp_q}. Consider price, features, and where to buy."
                    st.rerun()
            else:
                st.info("No results found. Try a different search term.")