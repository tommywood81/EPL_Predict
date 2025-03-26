import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model path - use absolute path for Heroku
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'elo_model.pkl')
    
    # Static files path
    STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    
    # Data directory
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Heroku specific settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True 