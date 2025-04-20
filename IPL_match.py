import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
matches = pd.read_csv("IPL_Matches_2022.csv")
team_balls = pd.read_csv("IPL_Ball_by_Ball_2022.csv")

st.set_page_config(page_title="IPL 2022", layout="wide")
st.image("ipl_image.png", width=200)
st.title("🏏 IPL 2022 Match Insights")

# Sidebar for page navigation
page = st.sidebar.radio("Navigate", ["Match Overview", "Batter Comparison", "Bowler Comparison", "Team Performance", "Player Impact"])

# Match selection
match_ids = matches['ID'].tolist()
match_id = st.sidebar.selectbox("Select Match ID:", match_ids)
match_info = matches[matches['ID'] == match_id].iloc[0]
team1 = match_info['Team1']
team2 = match_info['Team2']
venue = match_info['Venue']
match_balls = team_balls[team_balls['ID'] == match_id]

# Match Header
st.subheader(f"{team1} 🆚 {team2}")
st.caption(f"📍 Venue: {venue}")

# --- Match Overview Page ---
if page == "Match Overview":
    st.markdown("### 🧾 Match Summary")
    total_runs = match_balls.groupby('BattingTeam')['batsman_run'].sum()
    wickets = match_balls[match_balls['isWicketDelivery'] == 1].groupby('BattingTeam').size()
    overs = match_balls[match_balls['extra_type'].isnull()].groupby('BattingTeam').size() // 6

    summary = pd.DataFrame({
        "Runs": total_runs,
        "Wickets": wickets,
        "Overs": overs
    }).fillna(0)

    st.dataframe(summary)

# --- Batter Comparison Page ---
elif page == "Batter Comparison":
    st.markdown("### 🔍 Compare Two Batters")
    batters = match_balls['batter'].unique().tolist()
    col1, col2 = st.columns(2)

    with col1:
        player1 = st.selectbox("Select Player 1:", batters, index=0)
    with col2:
        player2 = st.selectbox("Select Player 2:", batters, index=1)

    p1_data = match_balls[match_balls['batter'] == player1]
    p2_data = match_balls[match_balls['batter'] == player2]

    comparison_df = pd.DataFrame({
        "Metric": ["Runs", "Balls Faced", "Strike Rate"],
        player1: [
            p1_data['batsman_run'].sum(),
            len(p1_data),
            (p1_data['batsman_run'].sum() / len(p1_data)) * 100 if len(p1_data) else 0
        ],
        player2: [
            p2_data['batsman_run'].sum(),
            len(p2_data),
            (p2_data['batsman_run'].sum() / len(p2_data)) * 100 if len(p2_data) else 0
        ]
    })

    st.table(comparison_df.set_index("Metric"))

    # Bar chart
    fig, ax = plt.subplots(figsize=(6, 3))
    metrics = ["Runs", "Balls Faced", "Strike Rate"]
    ax.bar(metrics, comparison_df[player1], width=0.3, label=player1, align='center')
    ax.bar(metrics, comparison_df[player2], width=0.3, label=player2, align='edge')
    ax.set_ylabel("Value")
    ax.set_title("Player Stats Comparison")
    ax.legend()
    st.pyplot(fig)

# --- Bowler Comparison Page ---
elif page == "Bowler Comparison":
    st.markdown("### 🎯 Compare Two Bowlers")
    bowlers = match_balls['bowler'].unique().tolist()
    col3, col4 = st.columns(2)

    with col3:
        bowler1 = st.selectbox("Select Bowler 1:", bowlers, index=0)
    with col4:
        bowler2 = st.selectbox("Select Bowler 2:", bowlers, index=1)

    def get_bowling_stats(df, bowler):
        data = df[df['bowler'] == bowler]
        runs_conceded = data['total_run'].sum()
        legal_deliveries = len(data[data['extra_type'].isnull()])
        overs = legal_deliveries // 6 + (legal_deliveries % 6) / 10
        wickets = len(data[data['isWicketDelivery'] == 1])
        economy = (runs_conceded / (legal_deliveries / 6)) if legal_deliveries else 0
        return runs_conceded, overs, wickets, economy

    b1_stats = get_bowling_stats(match_balls, bowler1)
    b2_stats = get_bowling_stats(match_balls, bowler2)

    bowler_df = pd.DataFrame({
        "Metric": ["Runs Conceded", "Overs", "Wickets", "Economy"],
        bowler1: b1_stats,
        bowler2: b2_stats
    }).set_index("Metric")

    st.table(bowler_df)

    # Chart
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    metrics2 = ["Runs Conceded", "Overs", "Wickets", "Economy"]
    ax2.bar(metrics2, bowler_df[bowler1], width=0.3, label=bowler1, align='center')
    ax2.bar(metrics2, bowler_df[bowler2], width=0.3, label=bowler2, align='edge')
    ax2.set_ylabel("Value")
    ax2.set_title("Bowler Stats Comparison")
    ax2.legend()
    st.pyplot(fig2)

# --- Player Impact Page ---
elif page == "Player Impact":
    st.markdown("### 🏏 Player Impact Index")
    players = match_balls['batter'].unique().tolist()
    player = st.selectbox("Select Player:", players)

    # Function to calculate Batting Impact (BPI)
    def calculate_batting_impact(runs, strike_rate, boundaries):
        return (runs * 0.5) + (strike_rate * 0.3) + (boundaries * 0.2)

    # Function to calculate Bowling Impact (BPI)
    def calculate_bowling_impact(wickets, economy_rate, dot_balls):
        # Ensure economy_rate is not zero to avoid division by zero error
        if economy_rate == 0:
            economy_rate = 1  # Set to a default value like 1 to avoid division by zero
        return (wickets * 0.4) + (1 / economy_rate * 0.4) + (dot_balls * 0.2)

    # Function to calculate Player Impact Index (PII)
    def calculate_player_impact_index(runs, strike_rate, boundaries, wickets, economy_rate, dot_balls):
        batting_impact = calculate_batting_impact(runs, strike_rate, boundaries)
        bowling_impact = calculate_bowling_impact(wickets, economy_rate, dot_balls)
        return (batting_impact * 0.6) + (bowling_impact * 0.4)

    # Get player-specific data
    player_data = match_balls[match_balls['batter'] == player]

    # Batting Stats
    runs = player_data['batsman_run'].sum()
    strike_rate = (runs / len(player_data)) * 100 if len(player_data) else 0
    boundaries = len(player_data[player_data['batsman_run'].isin([4, 6])])

    # Bowling Stats
    bowler_data = match_balls[match_balls['bowler'] == player]
    wickets = len(bowler_data[bowler_data['isWicketDelivery'] == 1])
    
    # Handle division by zero for economy rate
    if len(bowler_data) > 0:
        economy_rate = bowler_data['total_run'].sum() / (len(bowler_data) / 6) if len(bowler_data) else 0
    else:
        economy_rate = 0  # Handle case where player did not bowl

    # Handle dot balls
    dot_balls = len(bowler_data[bowler_data['batsman_run'] == 0])

    # Calculate Player Impact Index
    player_impact = calculate_player_impact_index(runs, strike_rate, boundaries, wickets, economy_rate, dot_balls)

    st.write(f"**Player Impact Index for {player}:** {player_impact:.2f}")

    
# --- Team Performance Page ---
elif page == "Team Performance":
    st.markdown("### 🧠 Team Summary")

    for team in [team1, team2]:
        st.markdown(f"#### 🏏 {team}")
        team_data = match_balls[match_balls['BattingTeam'] == team]
        total_runs = team_data['batsman_run'].sum()
        wickets = len(team_data[team_data['isWicketDelivery'] == 1])
        legal_deliveries = len(team_data[team_data['extra_type'].isnull()])
        overs = legal_deliveries // 6 + (legal_deliveries % 6) / 10
        run_rate = total_runs / (legal_deliveries / 6) if legal_deliveries else 0
        sixes = len(team_data[team_data['batsman_run'] == 6])
        fours = len(team_data[team_data['batsman_run'] == 4])

        st.write(f"**Runs Scored:** {total_runs}")
        st.write(f"**Wickets Lost:** {wickets}")
        st.write(f"**Overs Played:** {overs:.1f}")
        st.write(f"**Run Rate:** {run_rate:.2f}")
        st.write(f"**Fours:** {fours}, **Sixes:** {sixes}")
        st.markdown("---")

# Footer
st.markdown("---")
st.info("Built with 💖 Streamlit + Pandas + Matplotlib")
