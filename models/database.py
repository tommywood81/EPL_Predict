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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EloRating {self.rating} for {self.team.name}>'
    
    @classmethod
    def get_latest_ratings(cls):
        """Get the latest ELO rating for each team"""
        from sqlalchemy import func
        latest_ratings = db.session.query(
            cls.team_id,
            func.max(cls.timestamp).label('max_timestamp')
        ).group_by(cls.team_id).subquery()
        
        return cls.query.join(
            latest_ratings,
            (cls.team_id == latest_ratings.c.team_id) &
            (cls.timestamp == latest_ratings.c.max_timestamp)
        ).all() 