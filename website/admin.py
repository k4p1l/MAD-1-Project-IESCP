from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from .models import User, Influencer, AdRequest, Campaign, campaignRequest, Bookmark, Transaction, Rating
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .auth import role_required
from sqlalchemy.sql import func


admin = Blueprint('admin', __name__)


@admin.route('/dashboard')
@role_required('Admin')
@login_required
def dashboard():
    user_count = User.query.count()
    influencer_count = Influencer.query.count()
    sponsor_count = user_count - influencer_count
    campaign_count = Campaign.query.count()
    transaction_count = Transaction.query.count()
    total_transaction_amount = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    average_transaction_amount = db.session.query(db.func.avg(Transaction.amount)).scalar() or 0
    ad_request_count = AdRequest.query.count()
    average_influencer_balance = db.session.query(db.func.avg(Influencer.bank_account_balance)).scalar() or 0
    average_rating = db.session.query(db.func.avg(Rating.rating)).scalar() or 0


    campaigns_by_status = db.session.query(
        Campaign.status, db.func.count(Campaign.id)
    ).group_by(Campaign.status).all()
    labels_campaign_by_status=[campaign[0] for campaign in campaigns_by_status]
    values_campaign_by_status=[campaign[1] for campaign in campaigns_by_status]

    return render_template('Admin/dashboard.html',
                           user_count=user_count,
                           influencer_count=influencer_count,
                           sponsor_count=sponsor_count,
                           campaign_count=campaign_count,
                           transaction_count=transaction_count,
                           total_transaction_amount=total_transaction_amount,
                           average_transaction_amount=average_transaction_amount,
                           ad_request_count=ad_request_count,
                           average_influencer_balance=average_influencer_balance,
                           average_rating=average_rating,
                           labels_campaign_by_status=labels_campaign_by_status,
                           values_campaign_by_status=values_campaign_by_status
                           )

@admin.route('/influencer_stats')
@role_required('Admin')
@login_required
def influencer_stats():
    influencer_count = Influencer.query.count()
    most_used_platform= db.session.query(Influencer.platform, func.count(Influencer.platform)).group_by(Influencer.platform).order_by(func.count(Influencer.platform).desc()).first()
    most_populated_niche= db.session.query(Influencer.niche, func.count(Influencer.niche)).group_by(Influencer.niche).order_by(func.count(Influencer.niche).desc()).first()
    average_influencer_balance = db.session.query(db.func.avg(Influencer.bank_account_balance)).scalar() or 0
    influencers_by_niche= db.session.query(Influencer.niche, func.count(Influencer.niche)).group_by(Influencer.niche).all()
    influencers_by_platform= db.session.query(Influencer.platform, func.count(Influencer.platform)).group_by(Influencer.platform).all()
    average_influencer_reach= db.session.query(db.func.avg(Influencer.reach)).scalar() or 0

    return render_template('Admin/influencer_stats.html',influencer_count=influencer_count,
                           most_used_platform=most_used_platform,
                           most_populated_niche=most_populated_niche,
                           average_influencer_balance=average_influencer_balance,
                           influencers_by_niche=influencers_by_niche,
                           influencers_by_platform=influencers_by_platform,
                           average_influencer_reach=average_influencer_reach
                           )

@admin.route('/sponsor_stats')
@role_required('Admin')
@login_required
def sponsor_stats():
    influencer_count = Influencer.query.count()
    user_count = User.query.count()

    sponsor_count = user_count - influencer_count
    sponsor_by_niche= db.session.query(User.niche, func.count(User.niche)).group_by(User.niche).all()
    
    

    return render_template('Admin/sponsor_stats.html')

@admin.route('/transaction_stats')
@role_required('Admin')
@login_required
def transaction_stats():
    transaction_count = Transaction.query.count()
    total_transaction_amount = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    average_transaction_amount = db.session.query(db.func.avg(Transaction.amount)).scalar() or 0
    transaction_by_request_type= db.session.query(Transaction.request_type, func.count(Transaction.request_type)).group_by(Transaction.request_type).all()

    return render_template('Admin/transaction_stats.html')

@admin.route('/campaign_stats')
@role_required('Admin')
@login_required
def campaign_stats():
    campaigns_by_visibility = db.session.query(
        Campaign.visibility, db.func.count(Campaign.id)
    ).group_by(Campaign.visibility).all()

    campaigns_by_niche = db.session.query(
        Campaign.niche, db.func.count(Campaign.id)
    ).group_by(Campaign.niche).all()

    campaigns_by_status = db.session.query(
        Campaign.status, db.func.count(Campaign.id)
    ).group_by(Campaign.status).all()
    labels_campaign_by_status=[campaign[0] for campaign in campaigns_by_status]
    values_campaign_by_status=[campaign[1] for campaign in campaigns_by_status]

    average_campaign_budget= db.session.query(db.func.avg(Campaign.budget)).scalar() or 0
    bookmark_count = Bookmark.query.count()

    
    return render_template('Admin/campaign_stats.html', 
                            bookmark_count=bookmark_count,
                            campaigns_by_visibility=campaigns_by_visibility,
                            campaigns_by_niche=campaigns_by_niche,
                            campaigns_by_status=campaigns_by_status,
                            labels_campaign_by_status=labels_campaign_by_status,
                            values_campaign_by_status=values_campaign_by_status,
                            average_campaign_budget=average_campaign_budget)


