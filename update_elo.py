from app import app
from src.data_scraping import update_elo_data

with app.app_context():
    update_elo_data() 