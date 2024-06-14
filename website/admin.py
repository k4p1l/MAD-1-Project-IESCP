from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from .models import User, Influencer, AdRequest, Campaign, campaignRequest, Bookmark, Transaction, Rating
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from .auth import role_required
from sqlalchemy.sql import func


admin = Blueprint('admin', __name__)


@admin.route('/dashboard', methods=['GET', 'POST'])
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
    bookmark_count = Bookmark.query.count()
    average_influencer_balance = db.session.query(db.func.avg(Influencer.bank_account_balance)).scalar() or 0
    average_rating = db.session.query(db.func.avg(Rating.rating)).scalar() or 0

    campaigns_by_visibility = db.session.query(
        Campaign.visibility, db.func.count(Campaign.id)
    ).group_by(Campaign.visibility).all()

    campaigns_by_niche = db.session.query(
        Campaign.niche, db.func.count(Campaign.id)
    ).group_by(Campaign.niche).all()
    print(campaigns_by_niche)
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
                           bookmark_count=bookmark_count,
                           average_influencer_balance=average_influencer_balance,
                           average_rating=average_rating,
                           campaigns_by_visibility=campaigns_by_visibility,
                           campaigns_by_niche=campaigns_by_niche,
                           labels_campaign_by_status=labels_campaign_by_status,
                           values_campaign_by_status=values_campaign_by_status
                           )
