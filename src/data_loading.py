import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import logging

from src.error_reporting import log_error
from src.data_scraping import load_latest_elo_data, update_elo_data

# Configure logging
logger = logging.getLogger(__name__)

def load_match_data():
    """
    Load and preprocess match data.
    Remove unnecessary columns (e.g. date) for production.
    """
    try:
        datafile = 'data/raw/englandcsv.csv'
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
        logger.error(f"Error in load_match_data: {e}")
        return None

def load_elo_data():
    """
    Load Elo data, either from stored CSV or by scraping if data is old or missing.
    """
    try:
        # Try to load existing data
        df_elo = load_latest_elo_data()
        
        # If no data exists or data is older than 24 hours, scrape new data
        if df_elo is None:
            df_elo = update_elo_data()
            if df_elo is None:
                logger.error("Failed to load or update ELO data")
                return None
        
        # Standardize team names
        df_elo["team"] = df_elo["Team"].str.strip().str.replace(" ", "").str.lower()
        df_elo = df_elo.rename(columns={"Elo": "elorating"})
        df_elo = df_elo[["team", "elorating"]]
        
        return df_elo
    except Exception as e:
        logger.error(f"Error in load_elo_data: {e}")
        return None

def merge_data(match_df, elo_df):
    """
    Merge match data with Elo data for home and away teams.
    """
    try:
        if match_df is None or elo_df is None:
            logger.error("Cannot merge data: match_df or elo_df is None")
            return None
            
        # Merge Elo for home teams
        merged = match_df.merge(elo_df.rename(columns={'team': 'home_team', 'elorating': 'home_elo'}),
                                on='home_team', how='left')
        # Merge Elo for away teams
        merged = merged.merge(elo_df.rename(columns={'team': 'away_team', 'elorating': 'away_elo'}),
                              on='away_team', how='left')
        merged = merged.dropna(subset=['home_elo', 'away_elo'])
        return merged
    except Exception as e:
        logger.error(f"Error in merge_data: {e}")
        return None