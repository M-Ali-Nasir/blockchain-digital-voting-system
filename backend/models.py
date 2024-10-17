from extensions import db

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ethereum_address = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Options: 'voter' or 'admin'
    status = db.Column(db.String(50), nullable=False, default="active")  # 'active' or 'inactive'

# Candidate Model
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vote_count = db.Column(db.Integer, default=0)

# VoteLog Model
class VoteLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_address = db.Column(db.String(255), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    transaction_id = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())  # Timestamp of the vote
