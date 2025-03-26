import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:1RL7TY1RL7TY!@localhost/elo_predictor')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # Model path
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'elo_model.pkl')
    
    # Static files path
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    # Data directory
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') 