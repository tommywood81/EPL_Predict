import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from models.database import db, Team, EloRating
import logging

logger = logging.getLogger(__name__)

def get_elo_data():
    """
    Scrape ELO data from clubelo.com and return as DataFrame
    """
    url = "http://clubelo.com/ENG"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try different ways to find the table
        table = soup.find('table', {'class': 'table'})
        if not table:
            table = soup.find('table')
            
        if not table:
            raise ValueError("Could not find the table containing ELO data.")
            
        # Find all rows
        rows = table.find_all('tr')
        teams = []
        elos = []
        
        # Skip header row
        for row in rows[1:21]:  # Get first 20 teams
            cols = row.find_all('td')
            if len(cols) >= 2:
                team_name = cols[0].get_text(strip=True)
                elo_score = cols[1].get_text(strip=True)
                if team_name and elo_score:
                    teams.append(team_name)
                    elos.append(elo_score)
        
        if not teams or not elos:
            raise ValueError("No team data found in the table.")
            
        df_elo = pd.DataFrame({
            "Team": teams,
            "Elo": elos
        })
        
        # Clean up ELO scores
        df_elo["Elo"] = df_elo["Elo"].apply(lambda x: int(re.sub(r"[^\d]", "", x)))
        return df_elo
        
    except Exception as e:
        logger.error(f"Error scraping ELO data: {str(e)}")
        return None

def save_elo_data(df_elo):
    """
    Save ELO data to database
    """
    try:
        for _, row in df_elo.iterrows():
            team_name = row["Team"]
            elo_rating = row["Elo"]
            
            # Get or create team
            team = Team.query.filter_by(name=team_name).first()
            if not team:
                team = Team(name=team_name)
                db.session.add(team)
                db.session.flush()  # Get the team ID
            
            # Create new ELO rating
            rating = EloRating(team_id=team.id, rating=elo_rating)
            db.session.add(rating)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise e

def load_latest_elo_data():
    """
    Load the most recent ELO data from database
    Returns DataFrame with team names and ratings
    """
    try:
        latest_ratings = EloRating.get_latest_ratings()
        data = []
        for rating in latest_ratings:
            data.append({
                "Team": rating.team.name,
                "Elo": rating.rating
            })
        return pd.DataFrame(data)
    except Exception as e:
        raise e

def update_elo_data():
    """
    Main function to update ELO data
    Scrapes new data and saves it to database
    """
    try:
        df_elo = get_elo_data()
        save_elo_data(df_elo)
        return df_elo
    except Exception as e:
        print(f"Error updating ELO data: {e}")
        return None

if __name__ == "__main__":
    df = update_elo_data()
    if df is not None:
        print("Successfully updated ELO data:")
        print(df)