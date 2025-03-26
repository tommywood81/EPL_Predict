from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages
from src.data_loading import load_elo_data, merge_data, load_match_data
from src.prediction import get_team_list, predict_match, print_betting_odds, print_previous_matchups
from src.data_scraping import get_elo_data
from config import Config
import math
import pickle
import os
import joblib
import logging
from datetime import datetime
import sys
import pandas as pd

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize global variables
model = None
elo_data = None
match_data = None

def initialize_app():
    """Initialize the application by loading model and data"""
    global model, elo_data, match_data
    
    try:
        # Load model
        model_path = app.config['MODEL_PATH']
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            return False
            
        model = joblib.load(model_path)
        logger.info("Model loaded successfully")
        
        # Load ELO data
        elo_data = get_elo_data()
        if elo_data is None:
            logger.error("Failed to load ELO data")
            return False
        logger.info("ELO data loaded successfully")
        
        # Load match data
        match_data = load_match_data()
        if match_data is None:
            logger.error("Failed to load match data")
            return False
        logger.info("Match data loaded successfully")
                
        return True
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        return False

# Initialize the app
if not initialize_app():
    logger.error("Failed to initialize application")
    # Don't raise an exception, let the app start anyway

@app.route('/')
def index():
    """Render the home page"""
    try:
        teams = get_team_list(elo_data) if elo_data is not None else pd.DataFrame()
        return render_template('index.html', teams=teams)
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return render_template('error.html', error="An error occurred while loading the page"), 500

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
        # Get new ELO data
        new_elo_data = get_elo_data()
        if new_elo_data is None:
            return jsonify({'error': 'Failed to update ELO data'}), 500
            
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
