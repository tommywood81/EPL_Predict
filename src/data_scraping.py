import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db, Team, EloRating
from config import Config
from flask import Flask

def get_elo_data():
    """
    Scrape ELO data from clubelo.com and return as DataFrame
    """
    url = "http://clubelo.com/ENG"
    try:
        logger.info("Fetching data from clubelo.com...")
        response = requests.get(url)
        response.raise_for_status()
        
        logger.info("Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all table rows
        rows = soup.find_all('tr')
        
        teams = []
        elos = []
        seen_teams = set()  # Keep track of teams we've already processed
        
        # Loop through rows to find team data
        for row in rows:
            # Check if row contains team data (has a small tag with a number)
            small_tag = row.find('small')
            if small_tag and small_tag.text.strip().isdigit():
                # Get team name from the first link in the row
                team_link = row.find('a')
                if team_link:
                    team_name = team_link.text.strip()
                    # Skip if we've already seen this team
                    if team_name in seen_teams:
                        continue
                    seen_teams.add(team_name)
                    # Get ELO score from the right-aligned cell
                    elo_td = row.find('td', class_='r')
                    if elo_td:
                        elo_score = elo_td.text.strip()
                        teams.append(team_name)
                        elos.append(elo_score)
                        logger.info(f"Found team: {team_name} with ELO: {elo_score}")
        
        if not teams or not elos:
            logger.error("No team data found in the table")
            raise ValueError("No team data found in the table.")
            
        df_elo = pd.DataFrame({
            "Team": teams,
            "Elo": elos
        })
        
        # Clean up ELO scores
        df_elo["Elo"] = df_elo["Elo"].apply(lambda x: int(re.sub(r"[^\d]", "", x)))
        logger.info("Successfully created DataFrame with ELO data")
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
        logger.info("Successfully saved ELO data to database")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving ELO data: {str(e)}")
        raise e

def load_latest_elo_data():
    """
    Load the latest ELO data from the database
    """
    try:
        # Create Flask app and initialize database
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)
        
        with app.app_context():
            # Get the latest rating for each team
            latest_ratings = EloRating.get_latest_ratings()
            
            if not latest_ratings:
                logger.info("No ELO data found in database")
                return None
                
            # Convert to DataFrame
            teams = []
            elos = []
            for rating in latest_ratings:
                teams.append(rating.team.name)
                elos.append(rating.rating)
                
            df_elo = pd.DataFrame({
                "Team": teams,
                "Elo": elos
            })
            
            logger.info("Successfully loaded ELO data from database")
            return df_elo
            
    except Exception as e:
        logger.error(f"Error loading ELO data from database: {str(e)}")
        return None

def update_elo_data():
    """
    Main function to update ELO data
    Scrapes new data and saves it to database
    """
    try:
        # Create Flask app and initialize database
        app = Flask(__name__)
        app.config.from_object(Config)
        db.init_app(app)
        
        with app.app_context():
            df_elo = get_elo_data()
            if df_elo is not None:
                save_elo_data(df_elo)
                return df_elo
            return None
    except Exception as e:
        logger.error(f"Error updating ELO data: {str(e)}")
        return None

if __name__ == "__main__":
    df = update_elo_data()
    if df is not None:
        print("\nSuccessfully updated ELO data:")
        print(df)
    else:
        print("\nFailed to update ELO data. Check the logs above for details.")