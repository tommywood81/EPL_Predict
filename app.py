from flask import Flask, render_template, request
from src.data_loading import load_elo_data
from src.prediction import get_team_list, predict_match, print_betting_odds
import math
import pickle

app = Flask(__name__)

# Load your pre-trained model (adjust the filename/path as needed)
with open("models/elo_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route('/')
def index():
    # Load the ELO DataFrame
    elo_df = load_elo_data()
    # Optionally sort the teams for display
    team_list = get_team_list(elo_df)
    # Pass the team data as a list of dictionaries for the dropdowns
    elo_data = elo_df.to_dict(orient='records')
    return render_template('index.html', elo_data=elo_data)

@app.route('/predict', methods=['POST'])
def predict_route():
    elo_df = load_elo_data()
    
    # Retrieve selected teams from the form submission
    home_team = request.form.get('home_team')
    away_team = request.form.get('away_team')
    
    # Validate that two different teams are selected
    if home_team == away_team:
        error_message = "Home and Away teams cannot be the same."
        elo_data = elo_df.to_dict(orient='records')
        return render_template('index.html', elo_data=elo_data, error=error_message)
    
    # Get prediction result and team ratings from the prediction function
    prediction_result, home_rating, away_rating = predict_match(model, elo_df, home_team, away_team)
    
    # Convert prediction_result to a list if it's a NumPy array
    try:
        pred_list = prediction_result.tolist()
    except AttributeError:
        pred_list = prediction_result

    home_score = round(pred_list[0]) if isinstance(pred_list, (list, tuple)) and len(pred_list) > 0 else round(prediction_result)
    away_score = round(pred_list[1]) if isinstance(pred_list, (list, tuple)) and len(pred_list) > 1 else 0

    
    # Calculate the Elo difference
    elo_diff = home_rating - away_rating
    
    # Calculate win/draw/lose probabilities using a logistic-like function
    E_home = 1 / (1 + math.pow(10, -elo_diff / 400))
    P_draw = 0.30 * math.exp(-abs(elo_diff) / 400)
    P_home_win = E_home - 0.5 * P_draw
    P_away_win = 1 - P_home_win - P_draw

    # Calculate betting odds (decimal format)
    odds_home_win = 1 / P_home_win if P_home_win > 0 else float('inf')
    odds_draw = 1 / P_draw if P_draw > 0 else float('inf')
    odds_away_win = 1 / P_away_win if P_away_win > 0 else float('inf')
    
    # Prepare a dictionary of prediction results
    prediction_dict = {
        'home_score': home_score,
        'away_score': away_score,
        'elo_diff': round(elo_diff, 2),
        'home_rating': home_rating,
        'away_rating': away_rating,
        'home_prob': round(P_home_win * 100, 2),  # as percentage
        'draw_prob': round(P_draw * 100, 2),
        'away_prob': round(P_away_win * 100, 2),
        'odds_home_win': round(odds_home_win, 2),
        'odds_draw': round(odds_draw, 2),
        'odds_away_win': round(odds_away_win, 2)
    }
    
    # Pass the team list and prediction dictionary to the template
    elo_data = elo_df.to_dict(orient='records')
    return render_template('index.html', elo_data=elo_data, prediction=prediction_dict)

if __name__ == '__main__':
    app.run(debug=True)
