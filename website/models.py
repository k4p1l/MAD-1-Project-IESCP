from . import db
from sqlalchemy import Column, Integer, String, ForeignKey
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime



class User(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    role=  db.Column(db.String(20), nullable=True)
    niche= db.Column(db.String(100), nullable=True)
    influencers = relationship('Influencer', backref='user', lazy=True)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Integer , nullable=False) 
    visibility = db.Column(db.String(10), nullable=False)  # 'public' or 'private'
    goals = db.Column(db.Text, nullable=False)
    niche= db.Column(db.String(100), nullable=False)
    status= db.Column(db.String(100), nullable=False,default='Incomplete')
    flagged = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)


class Influencer(db.Model, UserMixin):
    __tablename__ = 'influencer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    profile_picture = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    platform= db.Column(db.String(100), nullable=False)
    bank_account_balance = db.Column(db.Float, default=0.0)
    flagged= db.Column(db.Boolean, default=False)


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    completed = db.Column(db.Boolean, default=False)
    completion_confirmed = db.Column(db.Boolean, default=False)
    payment_done=db.Column(db.Boolean, default=False)
    rating_done=db.Column(db.Boolean, default=False)


class campaignRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id= db.Column(db.Integer, db.ForeignKey('influencer.id'))
    messages = db.Column(db.Text)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    completed = db.Column(db.Boolean, default=False)
    completion_confirmed = db.Column(db.Boolean, default=False)
    payment_done=db.Column(db.Boolean, default=False)
    rating_done=db.Column(db.Boolean, default=False)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_request_id= db.Column(db.Integer, db.ForeignKey('ad_request.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=func.now())
    status=db.Column(db.Boolean,nullable=False, default=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_type=db.Column(db.String(150), nullable=False)
    influencer = relationship('Influencer', backref='transactions')
    ratings = db.relationship('Rating', backref='transaction', lazy=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ratee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    review = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=func.now())



