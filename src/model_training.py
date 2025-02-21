import os
import pickle
import sys
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

from error_reporting import log_error

# When splitting files, uncomment the next line:
# from error_reporting import log_error

def train_model(data):
    """
    Train a linear regression model to predict [fth_goals, fta_goals] from [home_elo, away_elo].
    """
    try:
        X = data[['home_elo', 'away_elo']]
        y = data[['fth_goals', 'fta_goals']].values
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        # Evaluate performance (for logging purposes)
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred, multioutput='uniform_average')
        mae_home = mean_absolute_error(y_test[:, 0], y_pred[:, 0])
        mae_away = mean_absolute_error(y_test[:, 1], y_pred[:, 1])
        print("\n--- Model Performance on Test Data (Unrounded) ---")
        print(f"R² Score (overall): {r2:.4f}")
        print(f"MAE Home Goals: {mae_home:.4f}, MAE Away Goals: {mae_away:.4f}")
        return model, X_train, X_test, y_train, y_test, data
    except Exception as e:
        log_error(f"Error in train_model: {e}")
        sys.exit(1)

def pickle_model(model, filename="models/elo_model.pkl"):
    """
    Pickle the trained model to disk.
    """
    try:
        os.makedirs("models", exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump(model, f)
        print(f"Model pickled to {filename}")
    except Exception as e:
        log_error(f"Error in pickle_model: {e}")

def load_model(filename="models/elo_model.pkl"):
    """
    Load a pickled model.
    """
    try:
        with open(filename, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        log_error(f"Error in load_model: {e}")
        sys.exit(1)