
import math
import numpy as np
from data_loading import load_match_data, load_elo_data, merge_data
from model_training import train_model, pickle_model, load_model
from prediction import get_team_list, prompt_user_for_teams, predict_match, print_previous_matchups, print_betting_odds


def main():
    # Load data
    match_df = load_match_data()
    elo_df = load_elo_data()
    merged_df = merge_data(match_df, elo_df)

    print(merged_df.head())


    # Train model and pickle it
    model, X_train, X_test, y_train, y_test, full_data = train_model(merged_df)
    pickle_model(model)

    # Get team list for user selection
    team_list = get_team_list(elo_df)

    print(elo_df)



    # Prompt user to select home and away teams
    home_team, away_team = prompt_user_for_teams(team_list)
    print(f"\nSelected Home Team: {home_team.title()}, Away Team: {away_team.title()}")

    # Load the model from pickle (simulate production loading)
    model_loaded = load_model()

    # Predict match score for the selected teams
    prediction, home_rating, away_rating = predict_match(model_loaded, elo_df, home_team, away_team)
    print(f"\nPrediction for match {home_team.title()} vs. {away_team.title()}:")
    print(f"Unrounded: Home predicted goals: {prediction[0]:.2f}, Away predicted goals: {prediction[1]:.2f}")
    print(f"(Home Elo: {home_rating}, Away Elo: {away_rating})")

    # Compute the rounded prediction:
    # Home goals are always rounded up and away goals are rounded normally.
    rounded_home = round(prediction[0])
    rounded_away = round(prediction[1])
    print(f"\nPredicted Result: {home_team.title()} {rounded_home} - {away_team.title()} {rounded_away}")

    # Print previous matchups from the merged dataset (which contains season and score)
    print_previous_matchups(merged_df, home_team, away_team)

    # --- Evaluate test set predictions with rounding adjustments ---
    y_pred_test = model_loaded.predict(X_test)

    # Unrounded accuracy metrics (already printed in train_model, but recomputed here for comparison)
    from sklearn.metrics import r2_score, mean_absolute_error  # In case not already imported
    r2_unrounded = r2_score(y_test, y_pred_test, multioutput='uniform_average')
    mae_home_unrounded = mean_absolute_error(y_test[:, 0], y_pred_test[:, 0])
    mae_away_unrounded = mean_absolute_error(y_test[:, 1], y_pred_test[:, 1])

    # Create rounded predictions: Home goals always rounded up, Away goals rounded normally.
    y_pred_rounded = np.copy(y_pred_test)
    y_pred_rounded[:, 0] = np.array([math.ceil(val) for val in y_pred_test[:, 0]])
    y_pred_rounded[:, 1] = np.array([round(val) for val in y_pred_test[:, 1]])

    r2_rounded = r2_score(y_test, y_pred_rounded, multioutput='uniform_average')
    mae_home_rounded = mean_absolute_error(y_test[:, 0], y_pred_rounded[:, 0])
    mae_away_rounded = mean_absolute_error(y_test[:, 1], y_pred_rounded[:, 1])

    print("\n--- Test Set Evaluation ---")
    print("Unrounded Predictions:")
    print(f"R² Score: {r2_unrounded:.4f}")
    print(f"MAE Home Goals: {mae_home_unrounded:.4f}, MAE Away Goals: {mae_away_unrounded:.4f}")
    print("\nRounded Predictions (Home: ceil, Away: round):")
    print(f"R² Score: {r2_rounded:.4f}")
    print(f"MAE Home Goals: {mae_home_rounded:.4f}, MAE Away Goals: {mae_away_rounded:.4f}")

    # --- Calculate Win/Draw/Lose Odds Based on Elo Difference ---
    dr = home_rating - away_rating
    E_home = 1 / (1 + math.pow(10, -dr/400))
    P_draw = 0.30 * math.exp(-abs(dr)/400)
    P_home_win = E_home - 0.5 * P_draw
    P_away_win = 1 - P_home_win - P_draw

    print("\n--- Win/Draw/Lose Odds Based on Elo Difference ---")
    print(f"Elo Difference (Home - Away): {dr:.2f}")
    print(f"Home Win Probability: {P_home_win*100:.2f}%")
    print(f"Draw Probability: {P_draw*100:.2f}%")
    print(f"Away Win Probability: {P_away_win*100:.2f}%")

    # --- Print Betting Odds (Decimal Format) ---
    print_betting_odds(dr)

if __name__ == "__main__":
    main()