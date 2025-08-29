import pandas as pd
import streamlit as st

st.title("NBA Player Stats Explorer")
st.markdown("""
This app performs simple web scraping of NBA player stats data!
* **Python libraries:** pandas, streamlit
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

st.sidebar.header("User Input Features")
selected_year = st.sidebar.selectbox("Year", list(reversed(range(1950, 2025))))

@st.cache_data
def load_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    tables = pd.read_html(url, header=0)
    target = None
    for t in tables:
        cols = t.columns.astype(str).str.strip().str.lower()
        if "player" in cols and ("tm" in cols or "team" in cols):
            target = t
            break
    if target is None:
        return pd.DataFrame(), None
    df = target.copy()
    if "Age" in df.columns:
        df = df[df["Age"] != "Age"]
    if "Rk" in df.columns:
        df = df.drop(columns=["Rk"])
    df = df.fillna(0)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )
    candidates = ["tm", "team"]
    team_col = next((c for c in candidates if c in df.columns), None)
    return df, team_col

playerstats, team_col = load_data(selected_year)

if playerstats.empty:
    st.error("No data table found for this season. The page format may have changed.")
else:
    if team_col and team_col in playerstats.columns:
        teams = pd.Series(playerstats[team_col]).replace("", pd.NA).dropna().astype(str).unique().tolist()
        teams = sorted(teams)
        selected_team = st.sidebar.multiselect("Team", teams, teams)
    else:
        st.error("Unable to determine the team column from scraped data.")
        selected_team = []
    unique_pos = ["C", "PF", "SF", "PG", "SG"]
    selected_pos = st.sidebar.multiselect("Position", unique_pos, unique_pos)
    if selected_team:
        playerstats = playerstats[playerstats[team_col].astype(str).isin(selected_team)]
    if selected_pos:
        playerstats = playerstats[playerstats["pos"].astype(str).isin(selected_pos)]
    st.header("NBA Player Stats by Team")
    st.dataframe(playerstats, use_container_width=True)
