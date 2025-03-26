from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages
from src.data_loading import load_elo_data, merge_data, load_match_data
from src.prediction import get_team_list, predict_match, print_betting_odds, print_previous_matchups
from src.data_scraping import update_elo_data
from models.database import db, migrate, EloRating
from config import Config
import math
import pickle
import os
import joblib
import logging

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

def load_model():
    """Load the model file if it exists."""
    global model
    try:
        if os.path.exists(Config.MODEL_PATH):
            model = joblib.load(Config.MODEL_PATH)
            logger.info("Model loaded successfully")
        else:
            logger.error(f"Model file not found at {Config.MODEL_PATH}")
            model = None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        model = None

def init_app():
    """Initialize the application."""
    try:
        # Create database tables
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Load the model
            load_model()
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")

# Initialize the app
init_app()

@app.route('/')
def index():
    """Home page route."""
    try:
        # Load ELO data
        elo_data = load_elo_data()
        if elo_data is None or elo_data.empty:
            flash('Error loading ELO data. Please try again later.', 'error')
            return render_template('index.html', teams=[], elo_data=None)
        
        # Get list of teams
        teams = get_team_list(elo_data)
        
        # Format elo_data for template
        elo_data_list = elo_data.to_dict('records')
        
        return render_template('index.html', teams=teams, elo_data=elo_data_list)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        flash('An error occurred. Please try again later.', 'error')
        return render_template('index.html', teams=[], elo_data=None)

@app.route('/predict', methods=['POST'])
def predict_route():
    """Handle match prediction requests."""
    try:
        if model is None:
            flash('Model not available. Please try again later.', 'error')
            return redirect(url_for('index'))
            
        home_team = request.form.get('home_team')
        away_team = request.form.get('away_team')
        
        if not home_team or not away_team:
            flash('Please select both home and away teams.', 'error')
            return redirect(url_for('index'))
            
        if home_team == away_team:
            flash('Please select different teams for home and away.', 'error')
            return redirect(url_for('index'))
        
        # Get prediction
        prediction = predict_match(model, home_team, away_team)
        if prediction is None:
            flash('Error making prediction. Please try again.', 'error')
            return redirect(url_for('index'))
            
        # Get betting odds
        odds = print_betting_odds(prediction)
        
        # Get previous matchups
        matchups = print_previous_matchups(home_team, away_team)
        
        return render_template('result.html', 
                             home_team=home_team,
                             away_team=away_team,
                             prediction=prediction,
                             odds=odds,
                             matchups=matchups)
    except Exception as e:
        logger.error(f"Error in predict route: {str(e)}")
        flash('An error occurred while making the prediction. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/update_elo', methods=['POST'])
def update_elo():
    """Handle ELO data update requests."""
    try:
        success = update_elo_data()
        if success:
            flash('ELO data updated successfully!', 'success')
        else:
            flash('Error updating ELO data. Please try again later.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in update_elo route: {str(e)}")
        flash('An error occurred while updating ELO data. Please try again.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
