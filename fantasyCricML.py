# 📦 Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

# 📂 Load Data
ball_df = pd.read_csv("IPL_Ball_by_Ball_2022.csv")
match_df = pd.read_csv("IPL_Matches_2022.csv")

# 🧹 Preprocess Match Data
match_df = match_df.dropna(subset=["Team1Players", "Team2Players"])

# 🎨 Page Setup
st.set_page_config(page_title="IPL Fantasy XI (2023)", layout="wide")
st.title("🏏 IPL 2023 Fantasy XI Recommender using ML")
st.markdown("Select two teams to get the top 11 players based on IPL 2022 stats with ML-based captain/vice-captain predictions!")

# 🧠 Team Selection
Team1 = st.selectbox("🅰️ Select Team 1", match_df['Team1'].unique())
Team2 = st.selectbox("🆚 Select Team 2", match_df['Team2'].unique())

# 📋 Extract player lists
sample_match = match_df[(match_df['Team1'] == Team1) & (match_df['Team2'] == Team2)].head(1)

if not sample_match.empty:
    team1_players = eval(sample_match.iloc[0]['Team1Players'])
    team2_players = eval(sample_match.iloc[0]['Team2Players'])
    selected_players = set(team1_players + team2_players)
else:
    st.error("❌ No match data found for selected teams!")
    st.stop()

# 📊 Batting Stats
batting_stats = ball_df.groupby('batter').agg({
    'batsman_run': 'sum',
    'ID': 'count'
}).reset_index().rename(columns={'batter': 'player', 'batsman_run': 'runs', 'ID': 'balls_faced'})

# 🎯 Bowling Stats
bowling_stats = ball_df[ball_df['isWicketDelivery'] == 1].groupby('bowler').agg({
    'isWicketDelivery': 'count',
    'ID': 'count'
}).reset_index().rename(columns={'bowler': 'player', 'isWicketDelivery': 'wickets', 'ID': 'balls_bowled'})

# 🧩 Merge & Clean
fantasy_df = pd.merge(batting_stats, bowling_stats, on='player', how='outer').fillna(0)

# 🧠 Fantasy Points Formula
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

# 🎯 Filter by selected teams
fantasy_df = fantasy_df[fantasy_df['player'].isin(selected_players)]

# 🧪 ML: Train simple regressor on all players (for captain prediction)
train_df = fantasy_df.copy()
X_train = train_df[['runs', 'wickets', 'balls_faced', 'balls_bowled']]
y_train = train_df['points']
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🧠 Predict fantasy points again for selected match
fantasy_df['predicted_points'] = model.predict(fantasy_df[['runs', 'wickets', 'balls_faced', 'balls_bowled']])

# 🏆 Pick XI
bats = fantasy_df[fantasy_df['role'] == 'Batsman'].sort_values('predicted_points', ascending=False).head(4)
bowls = fantasy_df[fantasy_df['role'] == 'Bowler'].sort_values('predicted_points', ascending=False).head(4)
allr = fantasy_df[fantasy_df['role'] == 'All-Rounder'].sort_values('predicted_points', ascending=False).head(3)
fantasy_xi = pd.concat([bats, bowls, allr]).sort_values('predicted_points', ascending=False).reset_index(drop=True)

# ⭐ Captain/Vice-Captain
captain = fantasy_xi.iloc[0]['player']
vice_captain = fantasy_xi.iloc[1]['player']

# 📋 Display XI
st.markdown(f"## 📋 Recommended Fantasy XI for **{Team1}** vs **{Team2}**")

for i in range(0, 11, 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(fantasy_xi):
            row = fantasy_xi.iloc[i + j]
            with cols[j]:
                st.markdown(f"### {row['player']}")
                st.markdown(f"**Role:** `{row['role']}`")
                st.markdown(f"🏏 Runs: `{int(row['runs'])}`")
                st.markdown(f"🎯 Wickets: `{int(row['wickets'])}`")
                st.markdown(f"🌟 Predicted Points: **{round(row['predicted_points'], 2)}**")

# 🧢 Captain & Vice-Captain
st.markdown("### 🧢 Captain & Vice-Captain Recommendation")
st.success(f"⭐ **Captain:** {captain}")
st.info(f"🌟 **Vice-Captain:** {vice_captain}")

# 🔝 Top Players
st.markdown("### 🔝 Top 10 Fantasy Players")
top_10 = fantasy_df.sort_values('predicted_points', ascending=False).head(10)
st.dataframe(top_10[['player', 'role', 'runs', 'wickets', 'predicted_points']].reset_index(drop=True))

# 📈 Distribution Plot
st.markdown("### 📈 Fantasy Points Distribution")
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(fantasy_df['predicted_points'], bins=30, kde=True, color="mediumseagreen", ax=ax)
ax.set_title("Distribution of Predicted Fantasy Points")
ax.set_xlabel("Points")
ax.set_ylabel("Number of Players")
st.pyplot(fig)

# 🔍 Player Search
st.markdown("### 🔍 Search for a Player")
search = st.text_input("Enter player name:")
if search:
    result = fantasy_df[fantasy_df['player'].str.contains(search, case=False)]
    if not result.empty:
        st.dataframe(result[['player', 'role', 'runs', 'wickets', 'predicted_points']])
    else:
        st.warning("No such player found.")

# 📄 Footer
st.markdown("---")
st.caption("📊 Based on IPL 2022 data | Created with ❤️ by Ayush Pandey")
