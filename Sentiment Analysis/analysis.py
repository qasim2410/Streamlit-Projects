import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os
import ast


# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="Airline Sentiment Dashboard", layout="wide")

# -------------------------------
# Load Data (auto-detect or upload)
# -------------------------------
DATA_URL = "Tweets.csv"

# If file not found locally, allow upload
if not os.path.exists(DATA_URL):
    st.warning("⚠️ `Tweets.csv` not found in this folder. Please upload the dataset.")
    uploaded_file = st.file_uploader("Upload Tweets.csv", type=["csv"])
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, encoding="utf-8", on_bad_lines="skip")
    else:
        st.stop()
else:
    data = pd.read_csv(DATA_URL, encoding="utf-8", on_bad_lines="skip")

# Guard for required column
if "airline_sentiment" not in data.columns:
    st.error("❌ Dataset must contain an 'airline_sentiment' column.")
    st.stop()

# Convert date column
if "tweet_created" in data.columns:
    data["tweet_created"] = pd.to_datetime(data["tweet_created"], errors="coerce")

# Extract lat/lon from tweet_coord if available
if "tweet_coord" in data.columns:
    coords = data["tweet_coord"].dropna().apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else None
    )
    coords = coords.dropna()
    if not coords.empty:
        data["lat"] = coords.apply(lambda x: x[0])
        data["lon"] = coords.apply(lambda x: x[1])

# -------------------------------
# Main App
# -------------------------------
st.title("✈️ Sentiment Analysis of Tweets about US Airlines")
st.sidebar.title("⚙️ Controls")

st.markdown("This is a **Streamlit dashboard** for analyzing airline tweet sentiments 🐦")

# ---------------- Random Tweet ----------------
st.sidebar.subheader("Show random tweet")
random_tweet = st.sidebar.radio("Sentiment", ("positive", "neutral", "negative"))
sample_tweet = data.query("airline_sentiment == @random_tweet")
if not sample_tweet.empty:
    st.sidebar.markdown(sample_tweet[["text"]].sample(n=1).iat[0, 0])
else:
    st.sidebar.warning("No tweet found for this sentiment!")

# ---------------- Sentiment Count ----------------
st.sidebar.markdown("### Number of tweets by sentiment")
select = st.sidebar.selectbox("Visualization type", ["Bar plot", "Pie chart"], key="1")
sentiment_count = data["airline_sentiment"].value_counts().reset_index()
sentiment_count.columns = ["Sentiment", "Tweets"]

if not st.sidebar.checkbox("Hide", True):
    st.markdown("### Number of tweets by sentiment")
    if select == "Bar plot":
        fig = px.bar(sentiment_count, x="Sentiment", y="Tweets", color="Tweets", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.pie(sentiment_count, values="Tweets", names="Sentiment")
        st.plotly_chart(fig, use_container_width=True)

# ---------------- Hourly Tweets ----------------
st.sidebar.subheader("When and where are users tweeting from?")
hour = st.sidebar.slider("Hour to look at", 0, 23)
if "tweet_created" in data.columns:
    modified_data = data[data["tweet_created"].dt.hour == hour]
else:
    modified_data = pd.DataFrame()

if not st.sidebar.checkbox("Close", True, key="2"):
    st.markdown("### Tweet locations based on time of day")
    st.markdown(f"{len(modified_data)} tweets between {hour}:00 and {(hour + 1) % 24}:00")
    if "lat" in modified_data.columns and "lon" in modified_data.columns:
        st.map(modified_data[["lat", "lon"]])
    else:
        st.info("⚠️ No coordinate data available in this dataset.")
    if st.sidebar.checkbox("Show raw data", False):
        st.write(modified_data)

# ---------------- Tweets per Airline ----------------
st.sidebar.subheader("Total number of tweets for each airline")
each_airline = st.sidebar.selectbox("Visualization type", ["Bar plot", "Pie chart"], key="3")
airline_sentiment_count = data.groupby("airline")["airline_sentiment"].count().sort_values(ascending=False).reset_index()
airline_sentiment_count.columns = ["Airline", "Tweets"]

if not st.sidebar.checkbox("Close", True, key="4"):
    st.subheader("Total number of tweets for each airline")
    if each_airline == "Bar plot":
        fig = px.bar(airline_sentiment_count, x="Airline", y="Tweets", color="Tweets", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.pie(airline_sentiment_count, values="Tweets", names="Airline")
        st.plotly_chart(fig, use_container_width=True)

# ---------------- Breakdown by Sentiment ----------------
st.sidebar.subheader("Breakdown airline by sentiment")
choice = st.sidebar.multiselect(
    "Pick airlines",
    ("US Airways", "United", "American", "Southwest", "Delta", "Virgin America"),
)

if len(choice) > 0:
    st.subheader("Breakdown airline by sentiment")
    breakdown_type = st.sidebar.selectbox("Visualization type", ["Pie chart", "Bar plot"], key="5")

    # Define subplot specs
    if breakdown_type == "Pie chart":
        specs = [[{"type": "domain"}] * len(choice)]
    else:
        specs = [[{"type": "xy"}] * len(choice)]

    fig = make_subplots(rows=1, cols=len(choice), subplot_titles=choice, specs=specs)

    for i, airline in enumerate(choice, start=1):
        df_sent = data[data["airline"] == airline]["airline_sentiment"].value_counts().reset_index()
        df_sent.columns = ["Sentiment", "Tweets"]

        if breakdown_type == "Bar plot":
            fig.add_trace(go.Bar(x=df_sent.Sentiment, y=df_sent.Tweets, showlegend=False), row=1, col=i)
        else:
            fig.add_trace(go.Pie(labels=df_sent.Sentiment, values=df_sent.Tweets, showlegend=True), row=1, col=i)

    fig.update_layout(height=600, width=1000)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Word Cloud ----------------
st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio("Display word cloud for what sentiment?", ("positive", "neutral", "negative"))
if not st.sidebar.checkbox("Close", True, key="6"):
    st.subheader(f"Word cloud for {word_sentiment} sentiment")
    df = data[data["airline_sentiment"] == word_sentiment]
    words = " ".join(df["text"].dropna())
    processed_words = " ".join(
        [word for word in words.split() if "http" not in word and not word.startswith("@") and word != "RT"]
    )
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=800, height=640).generate(processed_words)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
