import streamlit as st
import feedparser
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="OSINT Political Desk",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

.main-title{
    font-size:40px;
    font-weight:bold;
    color:#4da6ff;
}

.report{
    background:#111827;
    padding:20px;
    border-radius:10px;
    border-left:5px solid #3b82f6;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# GEMINI
# -----------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# -----------------------------
# FUNCTIONS
# -----------------------------
@st.cache_data(ttl=900)
def fetch_news(area):

    query = urllib.parse.quote(f"politics {area}")

    url = f"https://news.google.com/rss/search?q={query}"

    feed = feedparser.parse(url)

    news = []

    for article in feed.entries[:15]:
        news.append({
            "Title": article.title,
            "Source": getattr(article.source, "title", "Unknown"),
            "Published": article.published,
            "Link": article.link
        })

    return news


@st.cache_data(ttl=900)
def ai_report(area, news):

    headlines = "\n".join(
        [f"- {n['Title']}" for n in news]
    )

    prompt = f"""
You are a senior political intelligence analyst.

Analyze these headlines from {area}.

Return:

# Executive Summary

# Key Political Actors

# Emerging Risks

# Next Developments

{headlines}
"""

    model = genai.GenerativeModel("gemini-3.5-flash")

    return model.generate_content(prompt).text


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:

    st.title("🛰 Intelligence")

    area = st.text_input(
        "Target Area",
        "Meerut"
    )

    run = st.button("🚀 Scan")

    st.divider()

    st.write(datetime.now())


# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    '<p class="main-title">🌍 OSINT Political Desk</p>',
    unsafe_allow_html=True
)

st.caption("Open Source Political Intelligence Dashboard")

# -----------------------------
# LOAD
# -----------------------------
if run:

    with st.spinner("Scanning sources..."):

        news = fetch_news(area)

        report = ai_report(area, news)

    # -------------------------
    # METRICS
    # -------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Articles", len(news))
    c2.metric("Sources", len(set(n["Source"] for n in news)))
    c3.metric("Status", "LIVE")
    c4.metric("Threat", "🟡 Medium")

    st.divider()

    # -------------------------
    # TABS
    # -------------------------

    tab1, tab2, tab3 = st.tabs([
        "🧠 AI Report",
        "📊 Analytics",
        "📰 News Feed"
    ])

    # -------------------------
    # AI REPORT
    # -------------------------

    with tab1:

        st.markdown(
            f'<div class="report">{report}</div>',
            unsafe_allow_html=True
        )

        st.download_button(
            "Download Report",
            report,
            file_name="report.md"
        )

    # -------------------------
    # CHART
    # -------------------------

    with tab2:

        df = pd.DataFrame(news)

        chart = (
            df["Source"]
            .value_counts()
            .reset_index()
        )

        chart.columns = ["Source", "Articles"]

        fig = px.bar(
            chart,
            x="Source",
            y="Articles",
            title="Articles by Source"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -------------------------
    # NEWS
    # -------------------------

    with tab3:

        search = st.text_input("Search Headlines")

        for article in news:

            if search.lower() in article["Title"].lower():

                with st.expander(article["Title"]):

                    st.write("**Source:**", article["Source"])

                    st.write("**Published:**", article["Published"])

                    st.link_button(
                        "Read Article",
                        article["Link"]
                    )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()

st.caption("""
This dashboard uses public RSS news feeds and Google Gemini AI to generate political intelligence summaries. Always verify information with the original news sources.
""")