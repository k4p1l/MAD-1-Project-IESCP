import csv
import os
from datetime import datetime
from uuid import uuid4
from sqlalchemy import desc

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    abort,
    send_file,
    current_app,
)
from flask_login import login_required, current_user
from sqlalchemy.sql import func

from . import db
from .models import (
    Campaign,
    AdRequest,
    Influencer,
    campaignRequest,
    Transaction,
    Rating,
    Negotiation,
)
from .views import role_required

sponsor = Blueprint("sponsor", __name__)


# ---------- Sponsor Dashboard ------------------------#
@sponsor.route("/dashboard", methods=["GET", "POST"])
@role_required("Sponsor")
@login_required
def dashboard():
    active_campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    campaign_requests = (
        campaignRequest.query.join(Campaign)
        .filter(Campaign.user_id == current_user.id)
        .order_by(desc(campaignRequest.id))
        .all()
    )
    campaign_requests_with_details = []
    for campaign_request in campaign_requests:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        campaign_name = campaign.name
        influencer = Influencer.query.get(campaign_request.influencer_id)
        if influencer:
            influencer_name = influencer.name
            campaign_requests_with_details.append(
                {
                    "campaign_name": campaign_name,
                    "campaign_request": campaign_request,
                    "influencer_name": influencer_name,
                }
            )
        else:
            flash("Influencer not found", category="error")

    sent_requests = (
        AdRequest.query.join(Campaign)
        .filter(Campaign.user_id == current_user.id)
        .order_by(desc(AdRequest.id))
        .all()
    )
    sent_requests_with_details = []
    for sent_request in sent_requests:
        influencer = Influencer.query.get(sent_request.influencer_id)
        influencer_name = influencer.name
        sent_requests_with_details.append(
            {"ad_request": sent_request, "influencer_name": influencer_name}
        )
    return render_template(
        "Sponsor/dashboard.html",
        user=current_user,
        active_campaigns=active_campaigns,
        campaign_requests=campaign_requests_with_details,
        sent_requests=sent_requests_with_details,
    )


# ------------------- Campaign ------------------------#
@sponsor.route("/createCampaign", methods=["GET", "POST"])
@role_required("Sponsor")
@login_required
def createCampaign():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        budget = request.form.get("budget")
        visibility = request.form.get("visibility")
        goals = request.form.get("goals")
        niche = request.form.get("niche")
        user_id = current_user.id

        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=datetime.strptime(start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(end_date, "%Y-%m-%d"),
            budget=budget,
            visibility=visibility,
            goals=goals,
            niche=niche,
            user_id=user_id,
        )

        db.session.add(new_campaign)
        db.session.commit()
        flash("Campaign created successfully!", category="success")
        return redirect(url_for("sponsor.dashboard"))

    return render_template("Sponsor/campaignForm.html", user=current_user)


@sponsor.route("/viewCampaign/<int:campaign_id>", methods=["GET"])
@role_required("Sponsor")
@login_required
def viewCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaignRequests = (
        campaignRequest.query.filter_by(campaign_id=campaign_id)
        .order_by(desc(campaignRequest.id))
        .all()
    )

    campaign_requests_with_details = []
    for campaign_request in campaignRequests:
        influencer = Influencer.query.get(campaign_request.influencer_id)
        if influencer:
            influencer_name = influencer.name
            campaign_requests_with_details.append(
                {
                    "request": campaign_request,
                    "influencer_name": influencer_name,
                    "request_type": "Received",
                }
            )
        else:
            flash("Influencer not found", category="error")
    adrequests = (
        AdRequest.query.filter_by(campaign_id=campaign_id)
        .order_by(desc(AdRequest.id))
        .all()
    )
    sent_requests_with_details = []
    for sent_request in adrequests:
        adrequest_negotiations = sent_request.negotiations
        influencer = Influencer.query.get(sent_request.influencer_id)
        influencer_name = influencer.name
        pending_found = any(nego.status == "Pending" for nego in adrequest_negotiations)
        sent_requests_with_details.append(
            {
                "request": sent_request,
                "influencer_name": influencer_name,
                "request_type": "Sent",
                "negotiations": adrequest_negotiations,
                "pending_found": pending_found,
            }
        )

    return render_template(
        "Sponsor/viewCampaign.html",
        user=current_user,
        campaign=campaign,
        ad_requests=sent_requests_with_details,
        campaign_requests=campaign_requests_with_details,
    )


@sponsor.route("/viewCampaigns", methods=["GET"])
@role_required("Sponsor")
@login_required
def viewCampaigns():
    active_campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "Sponsor/viewCampaigns.html", user=current_user, campaigns=active_campaigns
    )


@sponsor.route("/deleteCampaign/<int:campaign_id>", methods=["POST"])
@role_required("Sponsor")
@login_required
def deleteCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.user_id != current_user.id:
        flash("You are not authorized to delete this campaign.", category="error")
        return redirect(url_for("sponsor.viewCampaigns"))
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign deleted successfully!", category="success")
    return redirect(url_for("sponsor.viewCampaigns"))


@sponsor.route("/editCampaign/<int:campaign_id>", methods=["GET", "POST"])
@role_required("Sponsor")
@login_required
def editCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    # Ensure the current user is the owner of the campaign
    if campaign.user_id != current_user.id:
        flash("You do not have permission to edit this campaign.", category="error")
        return redirect(url_for("sponsor.viewCampaigns"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        budget = request.form.get("budget")
        visibility = request.form.get("visibility")
        goals = request.form.get("goals")

        # Check for missing fields
        if not all(
            [name, description, start_date, end_date, budget, visibility, goals]
        ):
            flash("All fields are required.", category="error")
            return render_template("Sponsor/editCampaign.html", campaign=campaign)

        try:
            campaign.name = name
            campaign.description = description
            campaign.start_date = datetime.strptime(start_date, "%Y-%m-%d")
            campaign.end_date = datetime.strptime(end_date, "%Y-%m-%d")
            campaign.budget = budget
            campaign.visibility = visibility
            campaign.goals = goals

            db.session.commit()
            flash("Campaign updated successfully!", category="success")
            return redirect(url_for("sponsor.viewCampaigns"))
        except ValueError as e:
            flash(f"Invalid input: {e}", category="error")
            return render_template("Sponsor/editCampaign.html", campaign=campaign)
    return render_template("Sponsor/editCampaign.html", campaign=campaign)


# --------------------------------Adrequest-------------------------------------#
@sponsor.route("/campaign/<int:campaign_id>/create_ad_request", methods=["GET", "POST"])
@role_required("Sponsor")
@login_required
def create_ad_request(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == "POST":
        influencer_id = request.form["influencer_id"]
        messages = request.form["messages"]
        requirements = request.form["requirements"]
        payment_amount = request.form["payment_amount"]

        # Retrieve the influencer name from the influencer_id
        influencer = Influencer.query.get(influencer_id)
        if not influencer:
            flash("Influencer not found", "error")
            return redirect(url_for("sponsor.dashboard"))

        ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status="Pending",
        )
        db.session.add(ad_request)
        db.session.commit()
        flash("Ad request created successfully.", category="success")
        return redirect(url_for("sponsor.viewCampaign", campaign_id=campaign_id))

    # getting all influencers
    influencers = Influencer.query.all()

    return render_template(
        "Sponsor/create_ad_request.html", campaign=campaign, influencers=influencers
    )


@sponsor.route("/request_action/<int:request_id>/<action>", methods=["POST"])
@role_required("Sponsor")
@login_required
def request_action(request_id, action):
    ad_request = campaignRequest.query.get_or_404(request_id)
    if action == "accept":
        ad_request.status = "Accepted"
    elif action == "reject":
        ad_request.status = "Rejected"
    db.session.commit()
    flash(f"Request has been {action}ed.", category="success")
    return redirect(url_for("sponsor.dashboard"))


@sponsor.route("/ad_request/<int:ad_request_id>/delete", methods=["POST"])
@role_required("Sponsor")
@login_required
def delete_ad_request(ad_request_id):

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if not ad_request:
        ad_request = campaignRequest.query.get_or_404(ad_request_id)

    if ad_request.campaign.user_id != current_user.id:
        abort(403)

    db.session.delete(ad_request)
    db.session.commit()

    flash("Ad request deleted successfully.", category="success")
    return redirect(url_for("sponsor.dashboard"))


@sponsor.route("/view_completed_ad_requests/<int:campaign_id>")
@role_required("Sponsor")
@login_required
def view_completed_ad_requests(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaignRequests = campaignRequest.query.filter_by(
        campaign_id=campaign_id, completion_confirmed=True
    ).all()
    campaign_requests_with_details = []
    for campaign_request in campaignRequests:
        influencer = Influencer.query.get(campaign_request.influencer_id)
        if influencer:
            influencer_name = influencer.name
            campaign_requests_with_details.append(
                {
                    "request": campaign_request,
                    "influencer_name": influencer_name,
                    "request_type": "Received",
                }
            )
        else:
            flash("Influencer not found", category="error")

    adrequests = AdRequest.query.filter_by(
        campaign_id=campaign_id, completion_confirmed=True
    ).all()
    sent_requests_with_details = []
    for sent_request in adrequests:
        influencer = Influencer.query.get(sent_request.influencer_id)
        influencer_name = influencer.name
        sent_requests_with_details.append(
            {
                "request": sent_request,
                "influencer_name": influencer_name,
                "request_type": "Sent",
            }
        )
    return render_template(
        "Sponsor/view_completed_ad_requests.html",
        campaign=campaign,
        ad_requests=sent_requests_with_details,
        campaign_requests=campaign_requests_with_details,
    )


# ---------------------------------Influencers-----------------------------#
@sponsor.route("/campaign/<int:campaign_id>/browse_influencers")
@login_required
@role_required("Sponsor")
def browse_influencers(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    # Get parameters from the request
    reach = request.args.get("reach")
    niche = request.args.get("niche")
    name = request.args.get("name")

    # Base query
    query = Influencer.query

    # Apply filters if provided
    if reach:
        query = query.filter(Influencer.reach >= int(reach))
    if niche:
        query = query.filter(Influencer.niche == niche)
    if name:
        query = query.filter(Influencer.name.ilike(f"%{name}%"))

    # Execute the query
    filtered_influencers = query.all()
    return render_template(
        "Sponsor/browse_influencers.html",
        influencers=filtered_influencers,
        campaign=campaign,
    )


@sponsor.route("/view_all_influencers/<int:campaign_id>")
@role_required("Sponsor")
def view_all_influencers(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    influencers = Influencer.query.all()
    return render_template(
        "Sponsor/browse_influencers.html", influencers=influencers, campaign=campaign
    )


@sponsor.route(
    "/viewCampaign/<int:campaign_id>/<int:ad_request_id>/confirm_completion",
    methods=["POST"],
)
@role_required("Sponsor")
@login_required
def confirm_completion(campaign_id, ad_request_id):
    request_type = request.form.get("request_type")

    if request_type == "Sent":
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        if ad_request.completed == True:
            ad_request.completion_confirmed = True

    if request_type == "Received":
        campaign_request = campaignRequest.query.get_or_404(ad_request_id)
        if campaign_request.completed == True:
            campaign_request.completion_confirmed = True
    db.session.commit()
    flash("Ad request completed successfully.", category="success")
    return redirect(url_for("sponsor.viewCampaign", campaign_id=campaign_id))


# ---------------------------------Payment Gateway-----------------------------#
@sponsor.route("/payment_history/<int:user_id>")
@role_required("Sponsor")
@login_required
def payment_history(user_id):
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    transaction_with_details = []
    for transaction in transactions:
        influencer = Influencer.query.get(transaction.influencer_id)
        influencer_name = influencer.name
        influencer_platform = influencer.platform
        request_type = transaction.request_type
        if request_type == "Sent":
            ad_request = AdRequest.query.get(transaction.ad_request_id)
        elif request_type == "Received":
            ad_request = campaignRequest.query.get(transaction.ad_request_id)

        campaign_id = ad_request.campaign_id
        campaign = Campaign.query.get(campaign_id)
        campaign_name = campaign.name
        transaction_with_details.append(
            {
                "transaction": transaction,
                "influencer_name": influencer_name,
                "influencer_platform": influencer_platform,
                "campaign_name": campaign_name,
            }
        )
    return render_template(
        "sponsor/payment_history.html", transactions=transaction_with_details
    )


@sponsor.route("/make_payment/<int:ad_request_id>", methods=["GET", "POST"])
@role_required("Sponsor")
@login_required
def make_payment(ad_request_id):
    request_type = request.args.get("request_type")
    print(request_type)

    if request_type == "Sent":
        ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request_type == "Received":
        ad_request = campaignRequest.query.get_or_404(ad_request_id)

    influencer_id = ad_request.influencer_id
    influencer = Influencer.query.get_or_404(influencer_id)
    print(influencer.name)
    adrequest_with_details = {"request": ad_request, "influencer_name": influencer.name}

    if request.method == "GET":
        return render_template(
            "sponsor/make_payment.html", ad_request=adrequest_with_details
        )

    if request.method == "POST":
        card_number = request.form.get("card_number")
        expiration_date = request.form.get("expiration_date")
        cvv = request.form.get("cvv")

        # Validate card details
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            flash(
                "Invalid card number.Card number must be 16 digits.", category="error"
            )
        influencer_id = ad_request.influencer_id

        # Dummy payment processing
        transaction = Transaction(
            ad_request_id=ad_request.id,
            influencer_id=influencer_id,
            user_id=current_user.id,
            request_type=request_type,
            amount=ad_request.payment_amount,
            date=func.now(),
            status=True,
        )
        db.session.add(transaction)
        db.session.commit()
        print(ad_request.payment_done)
        ad_request.payment_done = True

        influencer = Influencer.query.get_or_404(influencer_id)
        influencer.bank_account_balance += ad_request.payment_amount
        db.session.commit()

        flash("Payment successful!", category="success")
        return redirect(url_for("sponsor.viewCampaigns"))
    return render_template(
        "sponsor/make_payment.html", ad_request=adrequest_with_details
    )


# ---------------------------------Export CSV-----------------------------#
@sponsor.route("/export_csv")
@role_required("Sponsor")
@login_required
def export_csv():
    user_id = current_user.id
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    transaction_with_details = []
    for transaction in transactions:
        influencer = Influencer.query.get(transaction.influencer_id)
        influencer_name = influencer.name
        influencer_platform = influencer.platform
        request_type = transaction.request_type
        if request_type == "Sent":
            ad_request = AdRequest.query.get(transaction.ad_request_id)
        elif request_type == "Received":
            ad_request = campaignRequest.query.get(transaction.ad_request_id)

        campaign_id = ad_request.campaign_id
        campaign = Campaign.query.get(campaign_id)
        campaign_name = campaign.name
        transaction_with_details.append(
            {
                "transaction": transaction,
                "influencer_name": influencer_name,
                "influencer_platform": influencer_platform,
                "campaign_name": campaign_name,
            }
        )
    filename = uuid4().hex + ".csv"
    url = "static/csv/" + filename
    filepath = os.path.join(current_app.root_path, "static", "csv", filename)
    Sno = 0

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Sno.",
                "Influencer Name",
                "Platform",
                "Campaign Name",
                "Request Type",
                "Amount",
                "Date",
            ]
        )
        for transaction in transaction_with_details:
            Sno += 1
            writer.writerow(
                [
                    Sno,
                    transaction["influencer_name"],
                    transaction["influencer_platform"],
                    transaction["campaign_name"],
                    transaction["transaction"].request_type,
                    transaction["transaction"].amount,
                    transaction["transaction"].date,
                ]
            )

    return send_file(filepath, as_attachment=True, download_name=filename)


# -------------------------------Ratings-----------------------------#
@sponsor.route("/view_ratings")
@role_required("Sponsor")
@login_required
def view_ratings():
    rater_id = current_user.id
    ratings = Rating.query.filter_by(rater_id=rater_id).all()
    ratings_with_details = []
    for rating in ratings:
        influencer = Influencer.query.get(rating.ratee_id)
        influencer_name = influencer.name
        ratings_with_details.append(
            {
                "rating": rating,
                "influencer_name": influencer_name,
            }
        )
    return render_template("sponsor/view_ratings.html", ratings=ratings_with_details)


@sponsor.route(
    "rate_influencer/<int:ad_request_id>/<string:request_type>", methods=["GET", "POST"]
)
@role_required("Sponsor")
@login_required
def rate_influencer(ad_request_id, request_type):
    transaction = Transaction.query.get_or_404(
        ad_request_id,
    )
    if request_type == "Sent":
        ad_request = AdRequest.query.get_or_404(ad_request_id)
    else:
        ad_request = None
    if request_type == "Received":
        ad_request = campaignRequest.query.get_or_404(ad_request_id)

    if transaction.user_id != current_user.id:
        flash("You are not authorized to rate this transaction.", "danger")
        return redirect(url_for("sponsor.dashboard"))
    influencer = Influencer.query.get_or_404(transaction.influencer_id)
    if request.method == "POST":
        rating_value = request.form.get("rating")
        review = request.form.get("review")

        new_rating = Rating(
            transaction_id=transaction.id,
            rater_id=current_user.id,
            ratee_id=transaction.influencer_id,
            rating=rating_value,
            review=review,
        )
        db.session.add(new_rating)
        ad_request.rating_done = True
        db.session.commit()
        flash("Rating submitted successfully.", "success")
        return redirect(url_for("sponsor.dashboard"))

    return render_template(
        "sponsor/rate_influencer.html",
        transaction=transaction,
        influencer_name=influencer.name,
    )


@sponsor.route(
    "/viewRequest/<string:request_type>/<int:ad_request_id>", methods=["GET", "POST"]
)
@role_required("Sponsor")
@login_required
def viewRequest(request_type, ad_request_id):
    if request_type == "Sent":
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        # get negotiation details from ad_request
        nego_details = ad_request.negotiations
    else:
        ad_request = None
    if request_type == "Received":
        ad_request = campaignRequest.query.get_or_404(ad_request_id)
        nego_details = ad_request.negotiations

    print(nego_details)

    return render_template(
        "sponsor/viewRequest.html", ad_request=ad_request, nego_details=nego_details
    )


# ---------------------------- Accept Negotiation ---------------------------- #
@sponsor.route("/accept_negotiation/<int:negotiation_id>>", methods=["POST"])
@role_required("Sponsor")
@login_required
def accept_negotiation(negotiation_id):
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    ad_request_id = negotiation.ad_request_id

    negotiation.status = "Accepted"
    db.session.commit()
    flash("Negotiation accepted successfully.", category="success")
    return redirect(url_for("sponsor.viewCampaigns"))


# ---------------------------- Reject Negotiation ---------------------------- #
@sponsor.route("/reject_negotiation/<int:negotiation_id>>", methods=["POST"])
@role_required("Sponsor")
@login_required
def reject_negotiation(negotiation_id):
    negotiation = Negotiation.query.get_or_404(negotiation_id)
    ad_request_id = negotiation.ad_request_id

    negotiation.status = "Rejected"
    db.session.commit()
    flash("Negotiation rejected successfully.", category="success")
    return redirect(url_for("sponsor.viewCampaigns"))
