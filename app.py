from flask import Flask, render_template, request
from src.data_loading import load_elo_data, merge_data, load_match_data
from src.prediction import get_team_list, predict_match, print_betting_odds, print_previous_matchups
import math
import pickle

app = Flask(__name__)

# Load your pre-trained model
with open("models/elo_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route('/')
def index():
    elo_df = load_elo_data()
    team_list = get_team_list(elo_df)
    elo_data = elo_df.to_dict(orient='records')
    return render_template('index.html', elo_data=elo_data)

@app.route('/predict', methods=['POST'])
def predict_route():
    elo_df = load_elo_data()
    
    # Retrieve selected teams from the form submission
    home_team = request.form.get('home_team').strip().replace(" ", "").lower()
    away_team = request.form.get('away_team').strip().replace(" ", "").lower()
    
    # Validate that two different teams are selected
    if home_team == away_team:
        error_message = "Home and Away teams cannot be the same."
        elo_data = elo_df.to_dict(orient='records')
        return render_template('index.html', elo_data=elo_data, error=error_message)
    
    # Get prediction result and team ratings from the prediction function
    prediction_result, home_rating, away_rating = predict_match(model, elo_df, home_team, away_team)
    
    # Convert prediction_result to a list if needed
    try:
        pred_list = prediction_result.tolist()
    except AttributeError:
        pred_list = prediction_result

    home_score = round(pred_list[0]) if isinstance(pred_list, (list, tuple)) and len(pred_list) > 0 else round(prediction_result)
    away_score = round(pred_list[1]) if isinstance(pred_list, (list, tuple)) and len(pred_list) > 1 else 0

    # Calculate the Elo difference and win/draw/lose probabilities
    elo_diff = home_rating - away_rating
    E_home = 1 / (1 + math.pow(10, -elo_diff / 400))
    P_draw = 0.30 * math.exp(-abs(elo_diff) / 400)
    P_home_win = E_home - 0.5 * P_draw
    P_away_win = 1 - P_home_win - P_draw

    # Get betting odds from the function
    betting_odds_list = print_betting_odds(elo_diff)
    betting_odds = "\n".join(betting_odds_list)
    
    # Load match data and merge to get previous matchups
    match_df = load_match_data()
    merged_df = merge_data(match_df, elo_df)
    previous_matchups_list = print_previous_matchups(merged_df, home_team, away_team)
    previous_matchups = "\n".join(previous_matchups_list)

    
    # Prepare a dictionary of prediction results
    prediction_dict = {
        'home_team': home_team.capitalize(),
        'away_team': away_team.capitalize(),
        'home_score': home_score,
        'away_score': away_score,
        'elo_diff': round(elo_diff, 2),
        'home_rating': home_rating,
        'away_rating': away_rating,
        'home_prob': round(P_home_win * 100, 2),
        'draw_prob': round(P_draw * 100, 2),
        'away_prob': round(P_away_win * 100, 2),
        'betting_odds': betting_odds,
        'previous_matchups': previous_matchups
    }
    
    elo_data = elo_df.to_dict(orient='records')
    return render_template('index.html', elo_data=elo_data, prediction=prediction_dict)

if __name__ == '__main__':
    app.run(debug=False)
