from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages
from src.data_loading import load_elo_data, merge_data, load_match_data
from src.prediction import get_team_list, predict_match, print_betting_odds, print_previous_matchups
from src.data_scraping import update_elo_data, get_elo_data, save_elo_data
from models.database import db, migrate, EloRating
from config import Config
import math
import pickle
import os
import joblib
import logging
from datetime import datetime
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)
migrate.init_app(app, db)

# Initialize global variables
model = None
elo_data = None
match_data = None

def initialize_app():
    """Initialize the application by loading model and data"""
    global model, elo_data, match_data
    
    try:
        # Load model
        model = joblib.load('models/elo_model.joblib')
        logger.info("Model loaded successfully")
        
        # Scrape and save ELO data
        elo_data = get_elo_data()
        if elo_data is not None:
            save_elo_data(elo_data)
            logger.info("ELO data scraped and saved successfully")
        else:
            logger.error("Failed to scrape ELO data")
            
        # Load match data
        match_data = load_match_data()
        if match_data is not None:
            logger.info("Match data loaded successfully")
        else:
            logger.error("Failed to load match data")
            
    except Exception as e:
        logger.error(f"Error initializing app: {e}")
        raise

# Initialize the app
initialize_app()

def get_last_update_time():
    """Get the timestamp of the most recent ELO update."""
    try:
        latest_rating = EloRating.query.order_by(EloRating.last_update.desc()).first()
        return latest_rating.last_update if latest_rating else None
    except Exception as e:
        logger.error(f"Error getting last update time: {str(e)}")
        return None

@app.route('/')
def index():
    """Home page route."""
    try:
        # Get team list
        team_list = get_team_list(elo_data)
        if team_list is None or team_list.empty:
            logger.error("Failed to get team list")
            return render_template('index.html', error="Failed to load team data")
            
        # Get last update time
        last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template('index.html', 
                             team_list=team_list,
                             last_update=last_update)
                             
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', error="An error occurred")

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        data = request.get_json()
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        custom_elos = data.get('custom_elos')
        
        if not home_team or not away_team:
            return jsonify({'error': 'Missing team data'}), 400
            
        # Get prediction
        prediction = predict_match(model, home_team, away_team, custom_elos)
        if prediction is None:
            return jsonify({'error': 'Failed to generate prediction'}), 500
            
        # Get previous matchups
        matchups = print_previous_matchups(match_data, home_team, away_team)
        prediction['previous_matchups'] = matchups
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error in predict route: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update_elo', methods=['POST'])
def update_elo():
    """Handle ELO update requests"""
    try:
        # Scrape new ELO data
        new_elo_data = get_elo_data()
        if new_elo_data is None:
            return jsonify({'error': 'Failed to update ELO data'}), 500
            
        # Save to database
        save_elo_data(new_elo_data)
        
        # Update global variable
        global elo_data
        elo_data = new_elo_data
        
        # Get updated team list
        team_list = get_team_list(elo_data)
        
        return jsonify({
            'success': True,
            'team_list': team_list.to_dict('records'),
            'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        logger.error(f"Error in update_elo route: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
