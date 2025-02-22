import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

from src.error_reporting import log_error

def load_match_data():
    """
    Load and preprocess match data.
    Remove unnecessary columns (e.g. date) for production.
    """
    try:
        datafile = 'data/raw/englandcsv.csv'



        """"""
        url = 'https://raw.githubusercontent.com/tommywood81/EPL_Predict/main/data/raw/epl_data.csv'

        """"""
        df = pd.read_csv(datafile)
        # Rename columns for consistency
        df = df.rename(columns={
            'Date': 'date',
            'FTH Goals': 'fth_goals',
            'FTA Goals': 'fta_goals',
            'FT Result': 'ft_result',
            'Season': 'season',
            'HomeTeam': 'home_team',
            'AwayTeam': 'away_team'
        })
        # Filter for seasons 2023/24 and 2024/25
        df = df[(df['season'] == '2023/24') | (df['season'] == '2024/25')]
        # Keep only necessary columns: team names, season, scores
        df = df[['season', 'home_team', 'away_team', 'fth_goals', 'fta_goals']]
        # Standardize team names
        df['home_team'] = df['home_team'].str.strip().str.replace(' ', '').str.lower()
        df['away_team'] = df['away_team'].str.strip().str.replace(' ', '').str.lower()
        return df
    except Exception as e:
        log_error(f"Error in load_match_data: {e}")
        sys.exit(1)

def load_elo_data():
    """
    Scrape Elo data from the given URL.
    This function locates the "Level 1 (20 teams)" header and scrapes
    the twenty team names and their Elo scores that follow.
    """
    try:
        url_elo = "http://clubelo.com/ENG"
        response = requests.get(url_elo)
        response.raise_for_status()  # Ensure we catch any HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the header row containing "Level 1 (20 teams)"
        header_i = soup.find("i", text=lambda t: "Level 1 (20 teams)" in t)
        if header_i:
            header_tr = header_i.find_parent("tr")
            # Get the next 20 rows after the header row
            team_rows = header_tr.find_next_siblings("tr")[:20]
        else:
            raise ValueError("Could not find the 'Level 1 (20 teams)' header.")

        teams = []
        elos = []
        # Loop through the twenty team rows and extract team name and Elo score
        for row in team_rows:
            a_tag = row.find("a")
            if a_tag:
                team_name = a_tag.get_text(strip=True)
                elo_td = row.find("td", class_="r")
                if elo_td:
                    elo_score = elo_td.get_text(strip=True)
                    teams.append(team_name)
                    elos.append(elo_score)

        # Create a DataFrame from the scraped data and rename columns accordingly
        df_elo = pd.DataFrame({
            "team": teams,
            "elorating": elos
        })

        # Clean the Elo values by removing any non-digit characters and converting to int
        df_elo["elorating"] = df_elo["elorating"].apply(lambda x: int(re.sub(r"[^\d]", "", x)))
        # Standardize team names: strip whitespace, remove spaces, and convert to lowercase
        df_elo["team"] = df_elo["team"].str.strip().str.replace(" ", "").str.lower()

        return df_elo
    except Exception as e:
        log_error(f"Error in load_elo_data: {e}")
        sys.exit(1)

def merge_data(match_df, elo_df):
    """
    Merge match data with Elo data for home and away teams.
    """
    try:
        # Merge Elo for home teams
        merged = match_df.merge(elo_df.rename(columns={'team': 'home_team', 'elorating': 'home_elo'}),
                                on='home_team', how='left')
        # Merge Elo for away teams
        merged = merged.merge(elo_df.rename(columns={'team': 'away_team', 'elorating': 'away_elo'}),
                              on='away_team', how='left')
        merged = merged.dropna(subset=['home_elo', 'away_elo'])
        return merged
    except Exception as e:
        log_error(f"Error in merge_data: {e}")
        sys.exit(1)