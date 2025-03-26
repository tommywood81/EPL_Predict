from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    elo_ratings = db.relationship('EloRating', backref='team', lazy=True)
    
    def __repr__(self):
        return f'<Team {self.name}>'

class EloRating(db.Model):
    __tablename__ = 'elo_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EloRating {self.rating} for {self.team.name}>'
    
    @classmethod
    def get_latest_ratings(cls):
        """Get the most recent rating for each team"""
        return cls.query.order_by(cls.team_id, cls.last_update.desc()).distinct(cls.team_id).all() 