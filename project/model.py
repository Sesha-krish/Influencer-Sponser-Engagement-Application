
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False)
    platform = db.Column(db.String(128), nullable=True)
    industry = db.Column(db.String(128), nullable=True)
    company = db.Column(db.String(128), nullable=True)
    niche = db.Column(db.String(128), nullable=True)
    rating = db.Column(db.String(128), nullable=True)
    profile_picture = db.Column(db.String(128), nullable=True)  
    ad_requests_sent = db.relationship('AdRequest', foreign_keys='AdRequest.sender_id', backref='sender', lazy=True)
    ad_requests_received = db.relationship('AdRequest', foreign_keys='AdRequest.receiver_id', backref='receiver', lazy=True)
    campaigns = db.relationship('Campaign', backref='user', lazy=True)


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_name = db.Column(db.String(128), nullable=False)
    ad_des = db.Column(db.String(256), nullable=True)
    ad_status = db.Column(db.String(64), nullable=False)
    payment = db.Column(db.Float, nullable=False)
    progress = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    des = db.Column(db.String(256), nullable=True)
    category = db.Column(db.String(128), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(64), nullable=True)
    products = db.Column(db.String(256), nullable=True)
    s_date = db.Column(db.Date, nullable=False)
    e_date = db.Column(db.Date, nullable=False)
    flagged = db.Column(db.String(64), nullable=True)
    flagreason = db.Column(db.String(64), nullable=True)
    camp_goal = db.Column(db.String(256), nullable=False)
    progress = db.Column(db.Float, nullable=True)
    adrequests = db.relationship('AdRequest', backref='campaign', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

from datetime import datetime

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_request.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    ad_request = db.relationship('AdRequest', backref='messages')
    campaign = db.relationship('Campaign', backref='messages')


