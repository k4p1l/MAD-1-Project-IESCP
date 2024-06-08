from flask import Blueprint, render_template, request, flash, redirect, url_for,abort
from .models import Campaign,AdRequest,User,Influencer,campaignRequest
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .auth import role_required


sponsor = Blueprint('sponsor', __name__)


@sponsor.route('/dashboard', methods=['GET', 'POST'])
@role_required('Sponsor')
@login_required
def dashboard():
    active_campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    campaign_requests = campaignRequest.query.join(Campaign).filter(Campaign.user_id == current_user.id).all()
    campaign_requests_with_details = []
    for campaign_request in campaign_requests:
        campaign=Campaign.query.get(campaign_request.campaign_id)
        campaign_name=campaign.name
        influencer=Influencer.query.get(campaign_request.influencer_id)
        if influencer:
            influencer_name=influencer.name
            campaign_requests_with_details.append({
                'campaign_name':campaign_name,
                'campaign_request': campaign_request,
                'influencer_name':influencer_name})
        else:
            flash('Influencer not found', category='error')

            
    sent_requests = AdRequest.query.join(Campaign).filter(Campaign.user_id == current_user.id).all()
    sent_requests_with_details = []
    for sent_request in sent_requests:
        influencer=Influencer.query.get(sent_request.influencer_id)
        influencer_name = influencer.name 
        sent_requests_with_details.append({
            'ad_request': sent_request,
            'influencer_name': influencer_name
        })
    return render_template('Sponsor/dashboard.html', user=current_user, active_campaigns=active_campaigns, campaign_requests=campaign_requests_with_details, sent_requests=sent_requests_with_details)


@sponsor.route('/createCampaign', methods=['GET', 'POST'])
@role_required('Sponsor')
@login_required
def createCampaign():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        goals = request.form.get('goals')
        user_id = current_user.id

        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=datetime.strptime(start_date, '%Y-%m-%d'),
            end_date=datetime.strptime(end_date, '%Y-%m-%d'),
            budget=budget,
            visibility=visibility,
            goals=goals,
            user_id=user_id)
        
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', category='success')
        return redirect(url_for('sponsor.dashboard'))
     
    return render_template("Sponsor/campaignForm.html", user=current_user)

@sponsor.route('/viewCampaign/<int:campaign_id>', methods=['GET'])
@role_required('Sponsor')
@login_required
def viewCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    adrequests=AdRequest.query.filter_by(campaign_id=campaign_id).all()
    sent_requests_with_details = []
    for sent_request in adrequests:
        influencer=Influencer.query.get(sent_request.influencer_id)
        influencer_name = influencer.name 
        sent_requests_with_details.append({
            'ad_request': sent_request,
            'influencer_name': influencer_name
        })

    return render_template('Sponsor/viewCampaign.html', campaign=campaign,ad_requests=sent_requests_with_details)

#to view all the campaigns list
@sponsor.route('/viewCampaigns', methods=['GET'])
@role_required('Sponsor')
@login_required
def viewCampaigns():
    active_campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template('Sponsor/viewCampaigns.html', campaigns=active_campaigns)

@sponsor.route('/deleteCampaign/<int:campaign_id>', methods=['POST'])
@role_required('Sponsor')
@login_required
def deleteCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash('You are not authorized to delete this campaign.', category='error')
        return redirect(url_for('sponsor.viewCampaigns'))

    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!', category='success')
    return redirect(url_for('sponsor.viewCampaigns'))

@sponsor.route('/editCampaign/<int:campaign_id>', methods=['GET', 'POST'])
@role_required('Sponsor')
@login_required
def editCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Ensure the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash('You do not have permission to edit this campaign.', category='error')
        return redirect(url_for('sponsor.viewCampaigns'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        goals = request.form.get('goals')

        # Check for missing fields
        if not all([name, description, start_date, end_date, budget, visibility, goals]):
            flash('All fields are required.', category='error')
            return render_template('Sponsor/editCampaign.html', campaign=campaign)
        
        try:
            campaign.name = name
            campaign.description = description
            campaign.start_date = datetime.strptime(start_date, '%Y-%m-%d')
            campaign.end_date = datetime.strptime(end_date, '%Y-%m-%d')
            campaign.budget = budget
            campaign.visibility = visibility
            campaign.goals = goals
            
            db.session.commit()
            flash('Campaign updated successfully!', category='success')
            return redirect(url_for('sponsor.viewCampaigns'))
        except ValueError as e:
            flash(f'Invalid input: {e}', category='error')
            return render_template('Sponsor/editCampaign.html', campaign=campaign)
    
    return render_template('Sponsor/editCampaign.html', campaign=campaign)

@sponsor.route('/campaign/<int:campaign_id>/create_ad_request', methods=['GET', 'POST'])
@role_required('Sponsor')
@login_required
def create_ad_request(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        influencer_id = request.form['influencer_id']
        messages = request.form['messages']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
    
       # Retrieve the influencer name from the influencer_id
        influencer = Influencer.query.get(influencer_id)
        if not influencer:
            flash('Influencer not found', 'error')
            return redirect(url_for('sponsor.dashboard'))

        ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status='Pending'
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad request created successfully.', category='success')
        return redirect(url_for('sponsor.viewCampaign', campaign_id=campaign_id))
    
    #getting all influencers
    influencers = Influencer.query.all()

    return render_template('Sponsor/create_ad_request.html', campaign=campaign, influencers=influencers)

@sponsor.route('/request_action/<int:request_id>/<action>', methods=['POST'])
@role_required('Sponsor')
@login_required
def request_action(request_id, action):
    ad_request = campaignRequest.query.get_or_404(request_id)
    if action == 'accept':
        ad_request.status = 'Accepted'
    elif action == 'reject':
        ad_request.status = 'Rejected'
    db.session.commit()
    flash(f'Request has been {action}ed.', category='success')
    return redirect(url_for('sponsor.dashboard'))

@sponsor.route('/campaign/<int:campaign_id>/browse_influencers')
@login_required
@role_required('Sponsor')
def browse_influencers(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

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
    return render_template('Sponsor/browse_influencers.html', influencers=filtered_influencers,campaign=campaign)

@sponsor.route('/view_all_influencers/<int:campaign_id>')
@role_required('Sponsor')
def view_all_influencers(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    # Logic to retrieve and display all influencers without any filters applied
    influencers = Influencer.query.all()
    return render_template('Sponsor/browse_influencers.html', influencers=influencers,campaign=campaign)

@sponsor.route('/ad_request/<int:ad_request_id>/delete', methods=['POST'])
@role_required('Sponsor')
@login_required
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    if ad_request.campaign.user_id != current_user.id:
        abort(403)
    
    db.session.delete(ad_request)
    db.session.commit()
    
    flash('Ad request deleted successfully.', category='success')
    return redirect(url_for('sponsor.dashboard'))