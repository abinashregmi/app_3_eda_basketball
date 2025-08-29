import base64
import pandas as pd
import streamlit as st

st.title("NBA Player Stats Explorer")
st.markdown("""
This app performs simple web scraping of NBA player stats data!
* **Python libraries:** base64, pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

st.sidebar.header("User Input Features")
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950, 2025))))

@st.cache_data
def load_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    html_tables = pd.read_html(url, header=0)
    df = html_tables[0]
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    playerstats.columns = (
        playerstats.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )
    team_col_candidates = ["tm", "team"]
    team_col = next((c for c in team_col_candidates if c in playerstats.columns), None)
    if not team_col:
        st.error("⚠️ No team column found in scraped data. The page format may have changed.")
        st.write("Available columns:", playerstats.columns.tolist())
        return playerstats, None
    return playerstats, team_col

playerstats, team_col = load_data(selected_year)

if team_col and team_col in playerstats.columns:
    sorted_unique_team = sorted(playerstats[team_col].unique())
    selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)
else:
    sorted_unique_team = []
    selected_team = []

if selected_team:
    playerstats = playerstats[playerstats[team_col].isin(selected_team)]

st.dataframe(playerstats)
