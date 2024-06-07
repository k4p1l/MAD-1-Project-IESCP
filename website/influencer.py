from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from .models import User
from .models import Influencer,AdRequest,Campaign,campaignRequest
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from .auth import role_required

influencer= Blueprint('influencer', __name__)



@influencer.route('/dashboard', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def dashboard():
    ad_requests = AdRequest.query.filter_by(influencer_name=Influencer.name).all()

    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None

    return render_template("Influencer/dashboard.html", user=current_user, influencer=influencer, ad_requests=ad_requests)

    
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
        user_id=request.form['user_id']
        platform=request.form.get('platform')

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            profile_picture.save(os.path.join(upload_folder, filename))
            profile_picture_path = os.path.join(upload_folder, filename)
        
            new_influencer = Influencer(name=name, email=email, profile_picture=filename, niche=niche, platform=platform, reach=reach,user_id=user_id)
            db.session.add(new_influencer)
            db.session.commit()
            flash('Influencer added successfully!', category='success')
            return redirect(url_for('influencer.viewInfluencers'))
        
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
        return redirect(url_for('influencer.viewInfluencers'))
    
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

@influencer.route('/ad_requests')
@role_required('Influencer')
@login_required
def view_ad_requests():
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    return render_template('Influencer/dashboard.html', ad_requests=ad_requests)

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

@influencer.route('/viewCampaigns')
@role_required('Influencer')
@login_required
def viewCampaigns():
    campaigns = Campaign.query.all()
    return render_template('Influencer/viewCampaigns.html', campaigns=campaigns)

@influencer.route('create_ad_request/<int:campaign_id>', methods=['GET', 'POST'])
@role_required('Influencer')
@login_required
def create_ad_request(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    
    if not campaign:
        flash('Campaign not found', 'error')
        return redirect(url_for('sponsor.dashboard'))
    
    if request.method == 'POST':
        influencer_name = request.form.get('influencer_name')
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amount = request.form.get('payment_amount')
        
        if not influencer_name:
            flash('Influencer name is required', 'error')
            return render_template('Influencer/create_ad_request.html', campaign=campaign)
        
        ad_request = campaignRequest(
            campaign_id=campaign.id,
            influencer_name=influencer_name,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount
        )
        
        db.session.add(ad_request)
        db.session.commit()
        
        flash('Ad request created successfully', category='success')
        return redirect(url_for('influencer.dashboard'))
    return render_template('Influencer/create_ad_request.html', campaign=campaign)

