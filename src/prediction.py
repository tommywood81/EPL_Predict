import math
import sys
import pandas as pd

from src.error_reporting import log_error

def get_team_list(elo_df):
    """
    Return a list of teams with their indices and Elo ratings.
    """
    team_list = elo_df.sort_values(by='elorating', ascending=False).reset_index(drop=True)
    team_list.index.name = "Index"
    print("\n--- Team List ---")
    print(team_list)
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

def predict_match(model, elo_df, home_team, away_team):
    """
    Look up Elo ratings for the given teams and predict the match score.
    """
    try:
        # Look up Elo ratings
        home_rating = float(elo_df.loc[elo_df['team'] == home_team, "elorating"])
        away_rating = float(elo_df.loc[elo_df['team'] == away_team, "elorating"])
        # Create feature vector (as a DataFrame with one row)
        features = pd.DataFrame([[home_rating, away_rating]], columns=['home_elo', 'away_elo'])
        prediction = model.predict(features)[0]
        return prediction, home_rating, away_rating
    except Exception as e:
        log_error(f"Error in predict_match: {e}")
        sys.exit(1)

def print_previous_matchups(data, home_team, away_team):
    print("DEBUG: Called print_previous_matchups()")
    results = []
    try:
        # Ensure both sides are compared in lowercase
        home_team_lower = home_team.lower()
        away_team_lower = away_team.lower()
        matchups = data[
            ((data['home_team'].str.lower() == home_team_lower) & (data['away_team'].str.lower() == away_team_lower)) |
            ((data['home_team'].str.lower() == away_team_lower) & (data['away_team'].str.lower() == home_team_lower))
        ]
        print("DEBUG: Number of matchups found:", len(matchups))
        if matchups.empty:
            results.append("No previous matchups found between these teams.")
        else:
            results.append("--- Previous Matchups ---")
            for idx, row in matchups.iterrows():
                season = row['season']
                results.append(f"Season: {season}, {row['home_team'].title()} {row['fth_goals']} - {row['fta_goals']} {row['away_team'].title()}")
    except Exception as e:
        results.append("Error occurred while retrieving previous matchups.")
        print("DEBUG: Exception in print_previous_matchups:", e)
    print("DEBUG: Returning results:", results)
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
