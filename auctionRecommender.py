# streamlit_app.py

import streamlit as st
import pandas as pd
import joblib

# Load the data and model
@st.cache_data
def load_data():
    return pd.read_csv("ipl_cleaned_data.xls")  # Make sure the file is CSV

@st.cache_resource
def load_model():
    return joblib.load("ipl_price_predictor.pkl")

# Skill keyword mapping for flexible filtering
skill_map = {
    "BATTER": ["BAT", "BATSMAN"],
    "BOWLER": ["BOWL", "BOWLER"],
    "ALLROUNDER": ["ALL", "ALLROUND", "ALL-ROUNDER"],
    "WICKETKEEPER": ["WK", "KEEP", "WICKET"]
}

# UI Inputs
st.title("🏏 IPL 2025 Auction Player Recommender")

team_name = st.text_input("Enter your Team Name")
budget = st.number_input("Enter your budget (in Lakh ₹)", min_value=10, value=500)
player_type = st.selectbox("Select required player type", ["BATTER", "BOWLER", "ALLROUNDER", "WICKETKEEPER"])
num_players = st.slider("Number of player recommendations", 1, 10, 5)

# Load data and model
df = load_data()
model = load_model()

# Filter by skill using keyword map
keywords = skill_map.get(player_type.upper(), [])
filtered = df[df["Skill"].str.upper().apply(lambda x: any(k in x for k in keywords))]

if filtered.empty:
    st.warning("⚠️ No players found for the selected type. Try a different skill.")
else:
    # Predict prices
    features = filtered[["Age", "Skill", "IPL Caps", "Player Status"]]
    estimated_prices = model.predict(features)
    filtered["Estimated Price (Lakh ₹)"] = estimated_prices

    # Calculate Player Score: value-for-money and experience
    filtered["Player Score"] = (
        filtered["IPL Caps"].fillna(0) * 2
        + (filtered["Estimated Price (Lakh ₹)"] - filtered["Base Price (Lakh)"]).clip(lower=0)
        - filtered["Age"].fillna(30) * 0.3
    )

    # Filter by budget before scoring
    filtered_budget = filtered[filtered["Estimated Price (Lakh ₹)"] <= budget]

    if filtered_budget.empty:
        st.warning("⚠️ No players found under the given budget.")
    else:
        shortlisted = filtered_budget.sort_values("Player Score", ascending=False).head(num_players)

        st.subheader("🎯 Top Value-for-Money Player Recommendations")
        st.dataframe(shortlisted[[
            "Player Name", "Skill", "Age", "IPL Caps", "Previous Teams",
            "Base Price (Lakh)", "Estimated Price (Lakh ₹)", "Player Score"
        ]])
