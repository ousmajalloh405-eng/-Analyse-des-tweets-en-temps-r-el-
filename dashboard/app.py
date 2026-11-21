"""Dashboard Streamlit temps réel sur MongoDB."""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import streamlit as st
from pymongo import MongoClient

st.set_page_config(page_title="Tweets Sentiment — Live", layout="wide")

MONGO_URI = os.getenv(
    "MONGO_URI", "mongodb://admin:changeme@localhost:27017/?authSource=admin"
)
MONGO_DB = os.getenv("MONGO_DB", "tweets")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "analyzed_tweets")


@st.cache_resource
def get_collection():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[MONGO_DB][MONGO_COLLECTION]


def fetch_df(limit: int = 5000) -> pd.DataFrame:
    coll = get_collection()
    cursor = coll.find({}, projection={"_id": 0}).sort("created_at", -1).limit(limit)
    docs = list(cursor)
    if not docs:
        return pd.DataFrame()
    df = pd.DataFrame(docs)
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    return df


st.title("📊 Analyse des tweets en temps réel")
st.caption("Kafka → Spark Structured Streaming → NLP → MongoDB")

placeholder = st.empty()
refresh_every = st.sidebar.slider("Rafraîchissement (s)", 2, 30, 5)
limit = st.sidebar.slider("Fenêtre (nb tweets)", 500, 20000, 5000, step=500)

while True:
    df = fetch_df(limit)

    with placeholder.container():
        if df.empty:
            st.info("Aucun tweet analysé pour l'instant. Lance le producteur puis le job Spark.")
        else:
            total = len(df)
            pos = int((df["sentiment"] == "positive").sum())
            neg = int((df["sentiment"] == "negative").sum())
            neu = int((df["sentiment"] == "neutral").sum())

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tweets traités", f"{total:,}")
            c2.metric("Positifs", f"{pos:,}", f"{pos/total:.1%}")
            c3.metric("Négatifs", f"{neg:,}", f"{neg/total:.1%}")
            c4.metric("Neutres", f"{neu:,}", f"{neu/total:.1%}")

            col_a, col_b = st.columns(2)

            with col_a:
                pie = px.pie(
                    names=["positive", "negative", "neutral"],
                    values=[pos, neg, neu],
                    color=["positive", "negative", "neutral"],
                    color_discrete_map={
                        "positive": "#2ca02c",
                        "negative": "#d62728",
                        "neutral": "#7f7f7f",
                    },
                    title="Répartition des sentiments",
                )
                st.plotly_chart(pie, use_container_width=True)

            with col_b:
                df["minute"] = df["created_at"].dt.floor("min")
                ts = (
                    df.groupby(["minute", "sentiment"])
                    .size()
                    .reset_index(name="count")
                )
                line = px.line(
                    ts, x="minute", y="count", color="sentiment",
                    title="Évolution des sentiments par minute",
                )
                st.plotly_chart(line, use_container_width=True)

            st.subheader("Top hashtags")
            exploded = (
                df["hashtags"]
                .fillna("")
                .str.split()
                .explode()
                .str.strip()
            )
            exploded = exploded[exploded.str.startswith("#") & (exploded != "")]
            top = exploded.value_counts().head(10)
            if not top.empty:
                st.plotly_chart(
                    px.bar(x=top.values, y=top.index, orientation="h",
                           labels={"x": "Occurrences", "y": "Hashtag"},
                           title="Top 10 hashtags"),
                    use_container_width=True,
                )
            else:
                st.write("Pas encore de hashtags.")

            st.subheader("Derniers tweets")
            st.dataframe(
                df[["created_at", "sentiment", "polarity", "text"]].head(20),
                use_container_width=True,
            )

    time.sleep(refresh_every)