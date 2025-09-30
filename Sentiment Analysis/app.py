import ast
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


# ---------- Configuration ----------
st.set_page_config(page_title="Sentiment Analysis of Tweets about US Airlines", layout="wide")

# Change this path to the location of your CSV file, or leave it as a Path and use the file uploader below
DATA_PATH = Path(r"C:\Users\qasim\OneDrive\Desktop\pr\streamlit-sentiment-dashboard\Tweets.csv")


# ---------- Load + prepare data ----------
@st.cache_data
def load_data(path: Path):
    df = pd.read_csv(path)

    # ensure tweet_created is parsed as datetime
    if 'tweet_created' in df.columns:
        df['tweet_created'] = pd.to_datetime(df['tweet_created'], errors='coerce')

    # parse tweet_coord (many public airline tweet CSVs use a string like "[lon, lat]")
    if 'tweet_coord' in df.columns:
        def parse_coord(x):
            if pd.isna(x):
                return (np.nan, np.nan)
            try:
                coords = ast.literal_eval(x)
                # many datasets store [lon, lat] -> convert to (lat, lon)
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    return (coords[1], coords[0])
            except Exception:
                # fallback: try simple split
                s = str(x).strip().strip('[]')
                parts = [p.strip() for p in s.split(',') if p.strip()]
                if len(parts) == 2:
                    try:
                        return (float(parts[1]), float(parts[0]))
                    except Exception:
                        return (np.nan, np.nan)
            return (np.nan, np.nan)

        coords = df['tweet_coord'].apply(parse_coord)
        df[['lat', 'lon']] = pd.DataFrame(coords.tolist(), index=df.index)

    # if dataset already has latitude/longitude columns, keep them (prefer existing ones)
    for lat_col, lon_col in [('latitude', 'longitude'), ('lat', 'lon')]:
        if lat_col in df.columns and lon_col in df.columns:
            df['lat'] = df.get('lat', df[lat_col])
            df['lon'] = df.get('lon', df[lon_col])
            break

    return df


# Allow user to upload a different CSV if they want
st.sidebar.markdown("**You can upload a different Tweets CSV (optional)**")
uploaded = st.sidebar.file_uploader("Upload Tweets CSV", type=['csv'])
if uploaded is not None:
    data = pd.read_csv(uploaded)
    # ensure datetime parsing and coordinate parsing as above
    if 'tweet_created' in data.columns:
        data['tweet_created'] = pd.to_datetime(data['tweet_created'], errors='coerce')
    if 'tweet_coord' in data.columns:
        def parse_coord_uploaded(x):
            if pd.isna(x):
                return (np.nan, np.nan)
            try:
                coords = ast.literal_eval(x)
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    return (coords[1], coords[0])
            except Exception:
                s = str(x).strip().strip('[]')
                parts = [p.strip() for p in s.split(',') if p.strip()]
                if len(parts) == 2:
                    try:
                        return (float(parts[1]), float(parts[0]))
                    except Exception:
                        pass
            return (np.nan, np.nan)
        coords = data['tweet_coord'].apply(parse_coord_uploaded)
        data[['lat', 'lon']] = pd.DataFrame(coords.tolist(), index=data.index)
else:
    # load from disk (cached)
    data = load_data(DATA_PATH)


# ---------- App layout ----------
st.title("Sentiment Analysis of Tweets about US Airlines")
st.sidebar.title("Sentiment Analysis Controls")
st.markdown("This application is a Streamlit dashboard used to analyze sentiments of tweets 🐦")


# --- Random tweet ---
st.sidebar.subheader("Show random tweet")
random_sentiment = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))
try:
    sample_texts = data.loc[data['airline_sentiment'] == random_sentiment, 'text']
    if sample_texts.empty:
        st.sidebar.write("No tweets available for that sentiment.")
    else:
        st.sidebar.markdown(sample_texts.sample(n=1).iat[0])
except KeyError:
    st.sidebar.write("Dataset doesn't contain an 'airline_sentiment' or 'text' column.")


# --- Number of tweets by sentiment ---
st.sidebar.markdown("### Number of tweets by sentiment")
vis_choice = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='vis_sent')
if 'airline_sentiment' in data.columns:
    sentiment_count = data['airline_sentiment'].value_counts().rename_axis('Sentiment').reset_index(name='Tweets')
else:
    sentiment_count = pd.DataFrame(columns=['Sentiment', 'Tweets'])

if not st.sidebar.checkbox("Hide sentiment chart", True, key='hide_sent'):
    st.markdown("### Number of tweets by sentiment")
    if vis_choice == 'Bar plot':
        fig = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig, use_container_width=True)


# --- When and where are users tweeting from? ---
st.sidebar.subheader("When and where are users tweeting from?")
hour = st.sidebar.slider("Hour to look at", 0, 23, 12)
if 'tweet_created' in data.columns:
    modified_data = data[data['tweet_created'].dt.hour == hour]
else:
    modified_data = pd.DataFrame()

if not st.sidebar.checkbox("Hide map", True, key='hide_map'):
    st.markdown("### Tweet locations based on time of day")
    st.markdown(f"{len(modified_data)} tweets between {hour}:00 and {(hour + 1) % 24}:00")

    if 'lat' in modified_data.columns and 'lon' in modified_data.columns:
        map_data = modified_data.dropna(subset=['lat', 'lon']).copy()
        if not map_data.empty:
            # st.map expects latitude/longitude column names or 'lat'/'lon' - rename to latitude/longitude
            st.map(map_data[['lat', 'lon']].rename(columns={'lat': 'latitude', 'lon': 'longitude'}))
        else:
            st.write("No geolocation data available for the selected hour.")
    else:
        st.write("Dataset does not contain location coordinates ('tweet_coord' or lat/lon columns).")

    if st.sidebar.checkbox("Show raw data", False, key='show_raw_map'):
        st.write(modified_data)


# --- Total number of tweets for each airline ---
st.sidebar.subheader("Total number of tweets for each airline")
air_vis = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='air_vis')
if 'airline' in data.columns:
    airline_sentiment_count = data['airline'].value_counts().rename_axis('Airline').reset_index(name='Tweets')
else:
    airline_sentiment_count = pd.DataFrame(columns=['Airline', 'Tweets'])

if not st.sidebar.checkbox("Hide airlines chart", True, key='hide_air'):
    st.subheader("Total number of tweets for each airline")
    if air_vis == 'Bar plot':
        fig_1 = px.bar(airline_sentiment_count, x='Airline', y='Tweets', color='Tweets', height=500)
        st.plotly_chart(fig_1, use_container_width=True)
    else:
        fig_2 = px.pie(airline_sentiment_count, values='Tweets', names='Airline')
        st.plotly_chart(fig_2, use_container_width=True)


# --- Breakdown airline by sentiment (small multiple / pie) ---
st.sidebar.subheader("Breakdown airline by sentiment")
available_airlines = sorted(data['airline'].dropna().unique()) if 'airline' in data.columns else []
choice = st.sidebar.multiselect('Pick airlines', available_airlines, key='breakdown_air')
if len(choice) > 0:
    st.subheader("Breakdown airline by sentiment")
    breakdown_type = st.sidebar.selectbox('Visualization type', ['Pie chart', 'Bar plot'], key='break_vis')
    n = len(choice)

    if breakdown_type == 'Bar plot':
        fig_3 = make_subplots(rows=1, cols=n, subplot_titles=choice)
        for j, airline in enumerate(choice):
            ct = data[data['airline'] == airline]['airline_sentiment'].value_counts().reset_index()
            ct.columns = ['Sentiment', 'Tweets']
            fig_3.add_trace(go.Bar(x=ct['Sentiment'], y=ct['Tweets'], showlegend=False), row=1, col=j + 1)
        fig_3.update_layout(height=400, width=min(1400, 300 * n))
        st.plotly_chart(fig_3, use_container_width=True)
    else:
        fig_3 = make_subplots(rows=1, cols=n, specs=[[{'type': 'domain'}] * n], subplot_titles=choice)
        for j, airline in enumerate(choice):
            ct = data[data['airline'] == airline]['airline_sentiment'].value_counts()
            fig_3.add_trace(go.Pie(labels=ct.index, values=ct.values, showlegend=(j == 0)), 1, j + 1)
        fig_3.update_layout(height=400, width=min(1400, 300 * n))
        st.plotly_chart(fig_3, use_container_width=True)


# --- Faceted histogram version ---
st.sidebar.subheader("Faceted histogram by airline and sentiment")
choice_hist = st.sidebar.multiselect('Pick airlines (histogram)', available_airlines, key='hist_air')
if len(choice_hist) > 0:
    choice_data = data[data['airline'].isin(choice_hist)]
    fig_0 = px.histogram(
        choice_data, x='airline', y='airline_sentiment', histfunc='count', color='airline_sentiment',
        facet_col='airline_sentiment', labels={'airline_sentiment': 'tweets'}, height=600
    )
    st.plotly_chart(fig_0, use_container_width=True)


# --- Word Cloud ---
st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', ('positive', 'neutral', 'negative'))
if not st.sidebar.checkbox("Hide word cloud", True, key='hide_wc'):
    st.subheader(f'Word cloud for {word_sentiment} sentiment')
    if 'airline_sentiment' in data.columns and 'text' in data.columns:
        df = data[data['airline_sentiment'] == word_sentiment]['text'].dropna().astype(str)
        words = ' '.join(df)
        processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
        if not processed_words.strip():
            st.write("No text available to build a word cloud for this sentiment.")
        else:
            wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=800, height=640).generate(processed_words)
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt.gcf())
    else:
        st.write("Dataset missing 'airline_sentiment' and/or 'text' columns.")


# ---------- Footer / tips ----------
st.markdown("---")
st.markdown("**Tips:** If the app errors on loading the CSV path, either upload a CSV using the uploader (sidebar) or update `DATA_PATH` at the top of the script to point to the correct file location.")
st.markdown("**Run:** `streamlit run streamlit_sentiment_app.py`")
