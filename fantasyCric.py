# 📦 Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📂 Load Data
ball_df = pd.read_csv("IPL_Ball_by_Ball_2022.csv")
match_df = pd.read_csv("IPL_Matches_2022.csv")

# 🎨 Page Setup
st.set_page_config(page_title="IPL 2023 Fantasy XI", layout="wide")
st.title("\U0001F3C6 IPL 2023 Fantasy XI Recommender")
st.markdown("Select two teams to generate the ideal fantasy XI based on 2022 performance \U0001F9E0")

# 🧠 Team Selection
teams = sorted(match_df['Team1'].unique())
Team1 = st.selectbox("\U0001F1E6 Select Team 1", teams)
Team2 = st.selectbox("\U0001F1FE Select Team 2", teams)

# 🧹 Filter relevant match player pool
team_matches = match_df[((match_df['Team1'] == Team1) & (match_df['Team2'] == Team2)) |
                        ((match_df['Team1'] == Team2) & (match_df['Team2'] == Team1))]
selected_ids = team_matches['ID'].unique()
filtered_balls = ball_df[ball_df['ID'].isin(selected_ids)]

# Batting stats
batting_stats = filtered_balls.groupby('batter').agg({
    'batsman_run': 'sum',
    'ID': 'count'
}).reset_index().rename(columns={'batter': 'player', 'batsman_run': 'runs', 'ID': 'balls_faced'})

# Bowling stats
bowling_stats = filtered_balls[filtered_balls['isWicketDelivery'] == 1].groupby('bowler').agg({
    'isWicketDelivery': 'count',
    'ID': 'count'
}).reset_index().rename(columns={'bowler': 'player', 'isWicketDelivery': 'wickets', 'ID': 'balls_bowled'})

# Merge batting and bowling stats
fantasy_df = pd.merge(batting_stats, bowling_stats, on='player', how='outer').fillna(0)

# 🎯 Calculate Fantasy Points
fantasy_df['points'] = (
    fantasy_df['runs'] +
    fantasy_df['wickets'] * 25 +
    (fantasy_df['runs'] // 4) +
    (fantasy_df['runs'] // 6) * 2
)

# 🧠 Role Classification
fantasy_df['role'] = fantasy_df.apply(
    lambda row: 'All-Rounder' if row['runs'] > 200 and row['wickets'] > 5 else (
        'Batsman' if row['runs'] > row['wickets'] * 20 else 'Bowler'
    ), axis=1
)

# Filter by players who played for either team in these matches
fantasy_df = fantasy_df[fantasy_df['points'] > 0]

# 🔍 Top players per role from selected matches only
bats = fantasy_df[fantasy_df['role'] == 'Batsman'].sort_values('points', ascending=False).head(4)
bowls = fantasy_df[fantasy_df['role'] == 'Bowler'].sort_values('points', ascending=False).head(4)
allr = fantasy_df[fantasy_df['role'] == 'All-Rounder'].sort_values('points', ascending=False).head(3)

fantasy_xi = pd.concat([bats, bowls, allr]).reset_index(drop=True)

# 📋 Fantasy XI Display
st.markdown(f"### \U0001F4CB Recommended Fantasy XI for **{Team1}** vs **{Team2}** (Based on IPL 2022 Head-to-Head Stats)")

# 🎴 Fancy Player Cards
for i in range(0, 11, 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(fantasy_xi):
            row = fantasy_xi.iloc[i + j]
            with cols[j]:
                st.markdown(f"### {row['player']}")
                st.markdown(f"**Role:** `{row['role']}`")
                st.markdown(f"\U0001F3CF Runs: `{int(row['runs'])}`")
                st.markdown(f"\U0001F3AF Wickets: `{int(row['wickets'])}`")
                st.markdown(f"\U0001F31F Fantasy Points: **{int(row['points'])}**")

# 📈 Fantasy Points Distribution
st.markdown("### \U0001F4C8 Fantasy Points Distribution")
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(fantasy_df['points'], bins=30, kde=True, color="skyblue", ax=ax)
ax.set_title("Distribution of Fantasy Points (Selected Match Players)")
ax.set_xlabel("Points")
ax.set_ylabel("Number of Players")
st.pyplot(fig)

# 🔍 Player Search
st.markdown("### \U0001F50E Search Player Performance")
search_name = st.text_input("Enter player name to search:")
if search_name:
    result = fantasy_df[fantasy_df['player'].str.contains(search_name, case=False)]
    if not result.empty:
        st.write(result[['player', 'role', 'runs', 'wickets', 'points']])
    else:
        st.warning("No player found.")

# 📄 Footer
st.markdown("---")
st.markdown("Made with ❤️ for IPL Fantasy Fans | Powered by 2022 IPL Stats")
