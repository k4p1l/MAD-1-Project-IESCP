from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, abort
from .models import User
from .models import Influencer, AdRequest, Campaign, campaignRequest, Bookmark, Transaction, Rating
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from .auth import role_required
from sqlalchemy.sql import func

influencer = Blueprint('influencer', __name__)


@influencer.route('/dashboard', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def dashboard():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    avg_rating_query = db.session.query(func.avg(Rating.rating).label('average_rating')).filter(
        Rating.ratee_id == influencer.id).first()
    average_rating = avg_rating_query.average_rating
    if influencer:
        ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
        campaignRequests = campaignRequest.query.filter_by(influencer_id=influencer.id).all()
        campaign_requests_with_details = []
        for campaign_request in campaignRequests:
            campaign = Campaign.query.get(campaign_request.campaign_id)
            if campaign:
                campaign_name = campaign.name
                campaign_requests_with_details.append({
                    'campaign_request': campaign_request,
                    'campaign_name': campaign_name
                })
            else:
                flash('Campaign not found', category='error')

        ad_requests_with_details = []
        for ad_request in ad_requests:
            campaign = Campaign.query.get(ad_request.campaign_id)
            user = User.query.get(campaign.user_id)
            ad_requests_with_details.append({
                'ad_request': ad_request,
                'campaign_name': campaign.name,
                'user_name': user.name
            })

        transactions = Transaction.query.filter_by(influencer_id=influencer.id).all()

        # Calculate total earnings
        total_earnings = sum(transaction.amount for transaction in transactions)
        return render_template("Influencer/dashboard.html", campaign_requests=campaign_requests_with_details,
                               user=current_user, influencer=influencer, ad_requests=ad_requests_with_details,
                               total_earnings=total_earnings, average_rating=average_rating)

    return render_template("Influencer/dashboard.html")


@influencer.route('/activeCampaigns', methods=['GET'])
@role_required('Influencer')
@login_required
def activeCampaigns():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id, completed=False).all()
    ad_requests_with_details = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        user = User.query.get(campaign.user_id)
        ad_requests_with_details.append({
            'request': ad_request,
            'campaign_name': campaign.name,
            'user_name': user.name,
            'request_type': 'Received'
        })

    campaign_requests = campaignRequest.query.filter_by(influencer_id=influencer.id, completed=False).all()
    campaign_requests_with_details = []
    for campaign_request in campaign_requests:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        user = User.query.get(campaign.user_id)
        campaign_requests_with_details.append({
            'request': campaign_request,
            'campaign_name': campaign.name,
            'user_name': user.name,
            'request_type': 'Sent'
        })
    return render_template("Influencer/activeCampaigns.html", user=current_user, influencer=influencer,
                           ad_requests=ad_requests_with_details, campaign_requests=campaign_requests_with_details)


@influencer.route('/view_completed_requests', methods=['GET'])
@role_required('Influencer')
@login_required
def view_completed_requests():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id, completed=True).all()
    ad_requests_with_details = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        user = User.query.get(campaign.user_id)
        ad_requests_with_details.append({
            'request': ad_request,
            'campaign_name': campaign.name,
            'user_name': user.name,
            'request_type': 'Received'
        })

    campaign_requests = campaignRequest.query.filter_by(influencer_id=influencer.id, completed=True).all()
    campaign_requests_with_details = []
    for campaign_request in campaign_requests:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        user = User.query.get(campaign.user_id)
        campaign_requests_with_details.append({
            'request': campaign_request,
            'campaign_name': campaign.name,
            'user_name': user.name,
            'request_type': 'Sent'
        })
    return render_template("Influencer/view_completed_requests.html", user=current_user, influencer=influencer,
                           ad_requests=ad_requests_with_details, campaign_requests=campaign_requests_with_details)


@influencer.route('/addInfluencer', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def addInfluencer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        profile_picture = request.files['profile_picture']
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        user_id = request.form['user_id']
        platform = request.form.get('platform')

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            profile_picture.save(os.path.join(upload_folder, filename))
            profile_picture_path = os.path.join(upload_folder, filename)

            new_influencer = Influencer(name=name, email=email, profile_picture=filename, niche=niche,
                                        platform=platform, reach=reach, user_id=user_id)
            db.session.add(new_influencer)
            db.session.commit()
            flash('Influencer added successfully!', category='success')
            return redirect(url_for('influencer.dashboard'))

        else:
            flash('Profile picture is required!', 'error')
    return render_template('Influencer/addInfluencer.html')


@influencer.route('/editInfluencer/<int:influencer_id>', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def editInfluencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)

    if request.method == 'POST':
        influencer.name = request.form['name']
        influencer.email = request.form['email']
        influencer.niche = request.form.get('niche')
        influencer.reach = request.form.get('reach')
        influencer.platform = request.form.get('platform')

        profile_picture = request.files['profile_picture']
        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(influencer.config['UPLOAD_FOLDER'], filename))
            influencer.profile_picture = filename

        db.session.commit()
        flash('Influencer updated successfully!', category='success')
        return redirect(url_for('influencer.dashboard'))

    return render_template('Influencer/editInfluencer.html', influencer=influencer)


@influencer.route('/viewInfluencers', methods=['GET'])
@role_required('Influencer')
@login_required
def viewInfluencers():
    # Get parameters from the request
    reach = request.args.get('reach')
    niche = request.args.get('niche')

    # Base query
    query = Influencer.query

    # Apply filters if provided
    if reach:
        query = query.filter(Influencer.reach >= int(reach))
    if niche:
        query = query.filter(Influencer.niche == niche)

    # Execute the query
    filtered_influencers = query.all()
    return render_template('Influencer/viewInfluencers.html', influencers=filtered_influencers)


@influencer.route('/view_all_influencers')
@role_required('Influencer')
def view_all_influencers():
    # Logic to retrieve and display all influencers without any filters applied
    influencers = Influencer.query.all()
    return render_template('Influencer/viewInfluencers.html', influencers=influencers)


@influencer.route('/viewInfluencer/<int:influencer_id>', methods=['GET'])
@role_required('Influencer')
@login_required
def viewInfluencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    return render_template('Influencer/viewInfluencer.html', influencer=influencer)


@influencer.route('/deleteInfluencer/<int:influencer_id>', methods=['POST'])
@role_required('Influencer')
@login_required
def deleteInfluencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    if influencer.user_id != current_user.id:
        flash('You are not authorized to delete this profile.', 'error')
        return redirect(url_for('influencer.viewInfluencers'))

    db.session.delete(influencer)
    db.session.commit()
    flash('Profile deleted successfully!', category='success')
    return redirect(url_for('influencer.dashboard'))


@influencer.route('/viewRequest/<int:ad_request_id>', methods=['GET'])
@role_required('Influencer')
@login_required
def viewRequest(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    # Retrieve the currently logged-in influencer
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()

    # Check if the ad request belongs to the currently logged-in influencer
    if ad_request.influencer_id != influencer.id:
        abort(403)

    campaign = Campaign.query.get(ad_request.campaign_id)
    user = User.query.get(campaign.user_id)

    ad_request_with_details = {
        'ad_request': ad_request,
        'campaign_name': campaign.name,
        'user_name': user.name
    }
    return render_template('Influencer/viewRequest.html', ad_request_details=ad_request_with_details)


@influencer.route('/edit_campaign_request/<int:campaign_request_id>', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def edit_campaign_request(campaign_request_id):
    campaign_request = campaignRequest.query.get_or_404(campaign_request_id)
    if request.method == 'POST':
        campaign_request.messages = request.form.get('messages')
        campaign_request.requirements = request.form.get('requirements')
        campaign_request.payment_amount = request.form.get('payment_amount')

        db.session.commit()
        flash('Campaign request updated successfully.', category='success')
        return redirect(url_for('influencer.dashboard'))
    return render_template('Influencer/edit_sent_request.html', campaign_request=campaign_request)


@influencer.route('/delete_campaign_request/<int:campaign_request_id>', methods=['POST'])
@role_required('Influencer')
@login_required
def delete_campaign_request(campaign_request_id):
    campaign_request = campaignRequest.query.get_or_404(campaign_request_id)
    db.session.delete(campaign_request)
    db.session.commit()
    flash('Campaign request deleted successfully.', category='success')
    return redirect(url_for('influencer.dashboard'))


@influencer.route('/ad_request/<int:ad_request_id>/accept', methods=['POST'])
@role_required('Influencer')
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = "Accepted"
    db.session.commit()
    flash('Ad request accepted successfully.', category='success')
    return redirect(url_for('influencer.dashboard'))


@influencer.route('/ad_request/<int:ad_request_id>/reject', methods=['POST'])
@role_required('Influencer')
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = "Rejected"
    db.session.commit()
    flash('Ad request rejected successfully.', category='success')
    return redirect(url_for('influencer.dashboard'))


@influencer.route('/viewCampaigns', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def viewCampaigns():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        campaigns = Campaign.query.filter(Campaign.name.ilike(f'%{search_query}%')).all()
    else:
        campaigns = Campaign.query.all()
    for campaign in campaigns:
        campaign.is_bookmarked = Bookmark.query.filter_by(user_id=current_user.id,
                                                          campaign_id=campaign.id).first() is not None
    return render_template('Influencer/viewCampaigns.html', campaigns=campaigns, influencer=influencer)


@influencer.route('/viewCampaign/<int:campaign_id>')
@role_required('Influencer')
@login_required
def viewCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template('Influencer/viewCampaign.html', campaign=campaign)


@influencer.route('create_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def create_ad_request(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()

    if not campaign:
        flash('Campaign not found', 'error')
        return redirect(url_for('sponsor.dashboard'))

    if request.method == 'POST':
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')

        if not influencer:
            flash('Influencer name is required', 'error')
            return render_template('Influencer/create_ad_request.html', campaign=campaign)

        ad_request = campaignRequest(
            campaign_id=campaign.id,
            influencer_id=influencer.id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount
        )

        db.session.add(ad_request)
        db.session.commit()

        flash('Ad request created successfully', category='success')
        return redirect(url_for('influencer.dashboard'))
    return render_template('Influencer/create_ad_request.html', campaign=campaign)


@influencer.route('/bookmark_campaign/<int:campaign_id>', methods=['POST'])
@role_required('Influencer')
@login_required
def bookmark_campaign(campaign_id):
    if request.method == 'POST':
        # Check if the campaign is already bookmarked
        bookmark = Bookmark.query.filter_by(user_id=current_user.id, campaign_id=campaign_id).first()
        if bookmark:
            # If already bookmarked, remove the bookmark
            db.session.delete(bookmark)
            db.session.commit()
        else:
            # If not bookmarked, create a new bookmark entry
            new_bookmark = Bookmark(user_id=current_user.id, campaign_id=campaign_id)
            db.session.add(new_bookmark)
            db.session.commit()
        return redirect(url_for('influencer.viewCampaigns', campaign_id=campaign_id))


@influencer.route('/view_bookmarks')
@role_required('Influencer')
@login_required
def view_bookmarks():
    campaigns = Campaign.query.all()
    for campaign in campaigns:
        campaign.is_bookmarked = Bookmark.query.filter_by(user_id=current_user.id,
                                                          campaign_id=campaign.id).first() is not None
    influencer_bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    bookmarked_campaigns = [Campaign.query.get(bookmark.campaign_id) for bookmark in influencer_bookmarks]

    return render_template('Influencer/Bookmarks.html', bookmarked_campaigns=bookmarked_campaigns, campaigns=campaigns)


@influencer.route('/search_campaigns', methods=['GET', 'POST'])
@login_required
@role_required('Influencer')
def search_campaigns():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        campaigns = Campaign.query.filter(Campaign.name.ilike(f'%{search_query}%')).all()
        for campaign in campaigns:
            campaign.is_bookmarked = Bookmark.query.filter_by(user_id=current_user.id,
                                                              campaign_id=campaign.id).first() is not None
        return render_template('Influencer/searchResults.html', campaigns=campaigns, search_query=search_query)
    return render_template('Influencer/viewCampaigns.html')


@influencer.route('/activeCampaigns/<int:ad_request_id>/mark_completed', methods=['POST'])
@login_required
@role_required('Influencer')
def mark_completed(ad_request_id):
    request_type = request.form.get('request_type')
    if request_type == 'Received':
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        if ad_request:
            ad_request.completed = True
            db.session.commit()
            flash('Ad request completed successfully.', category='success')

    if request_type == 'Sent':
        campaign_request = campaignRequest.query.get_or_404(ad_request_id)
        if campaign_request:
            campaign_request.completed = True
            db.session.commit()
            flash('Ad request completed successfully.', category='success')

    return redirect(url_for('influencer.dashboard'))


@influencer.route('/rate_sponsor/<int:ad_request_id>', methods=['GET', 'POST'])
@login_required
@role_required('Influencer')
def rate_sponsor(ad_request_id):
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    transaction = Transaction.query.get_or_404(ad_request_id)
    user = User.query.get_or_404(transaction.user_id)

    # Ensure that the current user is the influencer in the transaction
    if transaction.influencer_id != influencer.id:
        flash('You are not authorized to rate this transaction.', 'danger')
        return redirect(url_for('influencer.dashboard'))

    if request.method == 'POST':
        rating_value = request.form.get('rating')
        review = request.form.get('review')

        new_rating = Rating(
            transaction_id=transaction.id,
            rater_id=influencer.id,
            ratee_id=transaction.user_id,
            rating=rating_value,
            review=review
        )
        db.session.add(new_rating)
        db.session.commit()
        flash('Rating submitted successfully.', 'success')
        return redirect(url_for('influencer.dashboard'))

    return render_template('Influencer/rate_sponsor.html', transaction=transaction, user_name=user.name)


@influencer.route('/view_ratings')
@role_required('Influencer')
@login_required
def view_ratings():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    ratings = Rating.query.filter_by(ratee_id=influencer.id).all()
    return render_template('Influencer/view_ratings.html', ratings=ratings)
