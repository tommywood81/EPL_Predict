import math
import sys
import pandas as pd

from src.error_reporting import log_error

def get_team_list(elo_df):
    """
    Return a list of Premier League teams with their indices and Elo ratings.
    """
    # Filter for Premier League teams
    premier_league_teams = [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
        'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Forest',
        'Fulham', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
        'Sheffield United', 'Tottenham', 'West Ham', 'Wolves'
    ]
    
    # Filter DataFrame for Premier League teams
    team_list = elo_df[elo_df['Team'].isin(premier_league_teams)].copy()
    team_list = team_list.sort_values(by='Elo', ascending=False).reset_index(drop=True)
    team_list.index = team_list.index + 1  # Start index at 1
    team_list.index.name = "Index"
    return team_list

def prompt_user_for_teams(team_list):
    """
    Prompt the user to choose a home team and an away team based on the team index.
    """
    try:
        home_index = int(input("\nEnter the Index for the Home Team: "))
        away_index = int(input("Enter the Index for the Away Team: "))
        if home_index == away_index:
            raise ValueError("Home and Away team cannot be the same.")
        home_team = team_list.loc[home_index, "team"]
        away_team = team_list.loc[away_index, "team"]
        return home_team, away_team
    except Exception as e:
        log_error(f"Error in prompt_user_for_teams: {e}")
        sys.exit(1)

def predict_match(model, home_team, away_team, custom_elos=None):
    """
    Predict match outcome using the trained model and ELO ratings.
    
    Args:
        model: The trained model
        home_team: Name of the home team
        away_team: Name of the away team
        custom_elos: Dictionary of custom ELO ratings {team_name: rating}
    
    Returns:
        Dictionary containing prediction results
    """
    try:
        # Load ELO data
        elo_data = load_elo_data()
        if elo_data is None or elo_data.empty:
            return None
            
        # Get ELO ratings
        home_elo = None
        away_elo = None
        
        # Check for custom ELO ratings first
        if custom_elos:
            home_elo = custom_elos.get(home_team)
            away_elo = custom_elos.get(away_team)
        
        # If no custom ratings, use database values
        if home_elo is None or away_elo is None:
            home_row = elo_data[elo_data['Team'] == home_team]
            away_row = elo_data[elo_data['Team'] == away_team]
            
            if home_row.empty or away_row.empty:
                return None
                
            home_elo = home_row['Elo'].iloc[0]
            away_elo = away_row['Elo'].iloc[0]
        
        # Calculate ELO difference
        elo_diff = home_elo - away_elo
        
        # Prepare features for prediction
        # The model expects: [home_elo, away_elo, elo_diff]
        features = [[home_elo, away_elo, elo_diff]]
        
        # Get prediction
        prediction = model.predict(features)[0]
        
        # Calculate probabilities
        home_prob = round(prediction[0] * 100, 1)
        draw_prob = round(prediction[1] * 100, 1)
        away_prob = round(prediction[2] * 100, 1)
        
        # Calculate expected goals
        home_score = round(prediction[3], 1)
        away_score = round(prediction[4], 1)
        
        # Get betting odds and previous matchups
        odds = print_betting_odds({
            'home_prob': home_prob,
            'draw_prob': draw_prob,
            'away_prob': away_prob
        })
        
        matchups = print_previous_matchups(home_team, away_team)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'home_prob': home_prob,
            'draw_prob': draw_prob,
            'away_prob': away_prob,
            'elo_diff': elo_diff,
            'betting_odds': odds,
            'previous_matchups': matchups
        }
        
    except Exception as e:
        logger.error(f"Error in predict_match: {str(e)}")
        return None

def print_previous_matchups(data, home_team, away_team):
    results = []
    try:
        # Ensure both sides are compared in lowercase
        home_team_lower = home_team.lower()
        away_team_lower = away_team.lower()
        matchups = data[
            ((data['home_team'].str.lower() == home_team_lower) & (data['away_team'].str.lower() == away_team_lower)) |
            ((data['home_team'].str.lower() == away_team_lower) & (data['away_team'].str.lower() == home_team_lower))
        ]
        if matchups.empty:
            results.append("No previous matchups found between these teams.")
        else:
            results.append("--- Previous Matchups ---")
            for idx, row in matchups.iterrows():
                season = row['season']
                results.append(f"Season: {season}, {row['home_team'].title()} {row['fth_goals']} - {row['fta_goals']} {row['away_team'].title()}")
    except Exception as e:
        results.append("Error occurred while retrieving previous matchups.")
    return results

def print_betting_odds(elo_diff):
    """
    Return betting odds (in decimal format) for each outcome as a list of strings.
    """
    E_home = 1 / (1 + math.pow(10, -elo_diff / 400))
    P_draw = 0.30 * math.exp(-abs(elo_diff) / 400)
    P_home_win = E_home - 0.5 * P_draw
    P_away_win = 1 - P_home_win - P_draw

    odds_home_win = 1 / P_home_win if P_home_win > 0 else float('inf')
    odds_draw = 1 / P_draw if P_draw > 0 else float('inf')
    odds_away_win = 1 / P_away_win if P_away_win > 0 else float('inf')

    lines = []
    lines.append("--- Betting Odds (Decimal Format) ---")
    lines.append(f"Home Win Odds: {odds_home_win:.2f}")
    lines.append(f"Draw Odds: {odds_draw:.2f}")
    lines.append(f"Away Win Odds: {odds_away_win:.2f}")
    return lines
