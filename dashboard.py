import streamlit as st
import feedparser
import google.generativeai as genai
import urllib.parse

# --- CONFIGURATION ---
# Set page layout to wide like a real dashboard
st.set_page_config(page_title="Politi-Intel Dashboard", layout="wide")

# (In production, put your API key in Streamlit Secrets, not directly in the code)
FREE_GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=FREE_GEMINI_API_KEY)

# --- FUNCTIONS ---
def fetch_local_political_news(area):
    """Fetches news using Google News RSS based on area and politics"""
    query = f"politics {area}"
    safe_query = urllib.parse.quote(query)
    # Using Google News RSS (Free, no rate limit)
    url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:15]: # Get top 15 articles
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published
        })
    return articles

def generate_intelligence_brief(area, articles):
    """Uses Free Gemini AI to analyze the headlines and create a brief"""
    if not articles:
        return "No data found to analyze."
    
    # Combine headlines into one text block for the AI
    headlines = "\n".join([f"- {a['title']}" for a in articles])
    
    prompt = f"""
    You are an expert political intelligence analyst. I will give you recent news headlines for {area}.
    Please provide a concise intelligence brief for a dashboard. Include:
    1. Overall Political Climate (Tense, Cooperative, Election-focused, etc.)
    2. Key Entities (Names of politicians, parties, or organizations mentioned)
    3. Main Story Lines (2-3 bullet points summarizing the biggest issues)
    
    Here are the headlines:
    {headlines}
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# --- DASHBOARD UI ---
st.title("🌐 Political Intelligence Center")
st.markdown("Real-time local political monitoring powered by free APIs and AI.")

# User Input
area = st.text_input("Enter a City, State, or Country (e.g., Meerut, Texas, London):", "Meerut")

if st.button("Run Intelligence Scan"):
    with st.spinner(f"Gathering intelligence for {area}..."):
        
        # 1. Fetch Data
        articles = fetch_local_political_news(area)
        
        if articles:
            # 2. Get AI Analysis
            ai_brief = generate_intelligence_brief(area, articles)
            
            # 3. Display Data in Columns
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("🧠 AI Intelligence Brief")
                st.info(ai_brief)
                
            with col2:
                st.subheader("📰 Raw Intel Feed (Top Headlines)")
                for article in articles:
                    st.markdown(f"**[{article['title']}]({article['link']})**")
                    st.caption(f"📅 {article['published']}")
        else:
            st.error("No recent political news found for this area.")
