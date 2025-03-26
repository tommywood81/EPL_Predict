# EPL Match Predictor

A Flask web application that predicts English Premier League match outcomes using machine learning models and historical data.

## Features

- ELO rating system for team strength calculation
- Machine learning models for match prediction
- Historical match data analysis
- Web interface for predictions and analysis

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/EPL_Predict.git
cd EPL_Predict
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following content:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:your_password@localhost/elo_predictor
```

5. Set up the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Project Structure

- `app.py`: Main Flask application
- `models/`: Database models
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files
- `migrations/`: Database migration files
- `requirements.txt`: Python dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 