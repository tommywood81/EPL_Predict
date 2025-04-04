import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model():
    """Load the trained model"""
    try:
        model = joblib.load('models/elo_model.pkl')
        logger.info("Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def test_prediction(model):
    """Test prediction with sample data"""
    try:
        # Sample data for Liverpool vs Man City
        sample_data = {
            'home_elo': 2015,  # Liverpool's ELO
            'away_elo': 1917   # Man City's ELO
        }
        
        # Create feature array with only home_elo and away_elo
        features = [[sample_data['home_elo'], sample_data['away_elo']]]
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Print results
        logger.info("\nTest Prediction Results:")
        logger.info(f"Features used: {features[0]}")
        logger.info(f"Expected Home Goals: {prediction[0]:.1f}")
        logger.info(f"Expected Away Goals: {prediction[1]:.1f}")
        
        return True
    except Exception as e:
        logger.error(f"Error in test prediction: {e}")
        return False

def main():
    """Main function to test model predictions"""
    # Load model
    model = load_model()
    if model is None:
        logger.error("Failed to load model")
        return
    
    # Test prediction
    success = test_prediction(model)
    if success:
        logger.info("\nTest completed successfully")
    else:
        logger.error("\nTest failed")

if __name__ == "__main__":
    main() 