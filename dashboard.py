import streamlit as st
import feedparser
import google.generativeai as genai
import urllib.parse
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="OSINT Political Desk", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    /* Hide Streamlit default menu and footer for a whitelabeled look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style the AI report box */
    .report-box {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #0052cc;
        color: #FFFFFF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Clean up top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. API CONFIGURATION ---
try:
    # Fetch the API key securely from Streamlit Secrets
    FREE_GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    # Configure the AI engine with the key
    genai.configure(api_key=FREE_GEMINI_API_KEY)
    
except Exception:
    st.error("⚠️ API Key not found. Please configure st.secrets.")
    
# --- 4. CORE FUNCTIONS ---
@st.cache_data(ttl=900) # Caches data for 15 mins so you don't spam the RSS/API
def fetch_local_political_news(area):
    """Fetches top 15 news articles using Google News RSS"""
    query = f"politics {area}"
    safe_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:15]:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "source": entry.source.title if hasattr(entry, 'source') else "Unknown"
        })
    return articles

@st.cache_data(ttl=900)
def generate_intelligence_brief(area, articles):
    """Generates an executive summary using Gemini"""
    if not articles:
        return "No data available."
    
    headlines = "\n".join([f"- {a['title']} ({a['source']})" for a in articles])
    
    prompt = f"""
    You are an expert OSINT political analyst. Review the following recent headlines for {area}.
    Provide a professional, executive-level intelligence brief. Format it beautifully using Markdown.
    Include these exact headers:
    
    ### 🎯 Executive Summary
    (2-3 sentences summarizing the current political landscape)
    
    ### 🏛️ Key Entities Involved
    (Bullet points of politicians, parties, or groups mentioned)
    
    ### ⚠️ Emerging Storylines
    (Bullet points of the main political issues or conflicts)
    
    Headlines:
    {headlines}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"

# --- 5. SIDEBAR UI (CONTROLS) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Map_icons_by_Marius_Fiskum_16.svg/1024px-Map_icons_by_Marius_Fiskum_16.svg.png", width=60)
    st.title("Target Parameters")
    st.markdown("Configure your intelligence scan below.")
    
    area = st.text_input("📍 Target Area (City/State/Country):", "Meerut")
    
    run_scan = st.button("🚀 Initialize Scan", use_container_width=True, type="primary")
    
    st.divider()
    st.caption("Status: Secure Connection established.")
    st.caption(f"System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- 6. MAIN DASHBOARD UI ---
st.title(f"🌍 OSINT Political Desk: {area.upper()}")
st.markdown("Real-time open-source intelligence monitoring and automated AI analysis.")
st.divider()

if run_scan or area:
    with st.spinner(f"Intercepting signals for {area}..."):
        articles = fetch_local_political_news(area)
        
        if articles:
            # Dashboard Metrics Row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="📡 Sources Scanned", value=len(articles))
            with col2:
                st.metric(label="🕒 Latest Intel", value="Just Now", delta="Live")
            with col3:
                st.metric(label="🧠 AI Status", value="Active", delta="Ready", delta_color="normal")
            
            st.write("") # Spacer
            
            # Use Tabs to separate AI Analysis from Raw Data
            tab1, tab2 = st.tabs(["🧠 AI Intelligence Brief", "📰 Raw Signal Feed (Links)"])
            
            with tab1:
                ai_brief = generate_intelligence_brief(area, articles)
                # Displaying the AI output inside a styled HTML div
                st.markdown(f'<div class="report-box">{ai_brief}</div>', unsafe_allow_html=True)
                
            with tab2:
                # Display raw data neatly
                for i, article in enumerate(articles):
                    with st.expander(f"🔹 {article['title']}"):
                        st.write(f"**Source:** {article['source']}")
                        st.write(f"**Published:** {article['published']}")
                        st.markdown(f"[🔗 Read Full Source Article]({article['link']})")
        else:
            st.warning(f"No recent political signals detected for {area}.")


# --- FOOTER / DISCLAIMER ---
st.divider()
st.caption("""
**Disclaimer:** This is a public Open Source Intelligence (OSINT) dashboard. 
The executive summaries are generated automatically by AI (Google Gemini) based on recent RSS news feeds. 
Always verify political news with the raw source links provided in the 'Raw Signal Feed' tab.
""")
