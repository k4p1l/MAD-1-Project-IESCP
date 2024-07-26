from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    abort,
)
from .models import User
from .models import (
    Influencer,
    AdRequest,
    Campaign,
    campaignRequest,
    Bookmark,
    Transaction,
    Rating,
    Negotiation,
)
from . import db
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .views import role_required
from sqlalchemy.sql import func
from sqlalchemy import desc

influencer = Blueprint("influencer", __name__)


# ---------------INFLUENCER CRUD-------------------#
@influencer.route("/addInfluencer", methods=["GET", "POST"])
@role_required("Influencer")
@login_required
def addInfluencer():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        profile_picture = request.files["profile_picture"]
        niche = request.form.get("niche")
        reach = request.form.get("reach")
        user_id = request.form["user_id"]
        platform = request.form.get("platform")

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            upload_folder = current_app.config["UPLOAD_FOLDER"]

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            profile_picture.save(os.path.join(upload_folder, filename))
            profile_picture_path = os.path.join(upload_folder, filename)

            new_influencer = Influencer(
                name=name,
                email=email,
                profile_picture=filename,
                niche=niche,
                platform=platform,
                reach=reach,
                user_id=user_id,
            )
            db.session.add(new_influencer)
            db.session.commit()
            flash("Influencer added successfully!", category="success")
            return redirect(url_for("influencer.dashboard"))

        else:
            flash("Profile picture is required!", "error")
    return render_template("Influencer/addInfluencer.html")


@influencer.route("/editInfluencer/<int:influencer_id>", methods=["GET", "POST"])
@role_required("Influencer")
@login_required
def editInfluencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)

    if request.method == "POST":
        influencer.name = request.form["name"]
        influencer.email = request.form["email"]
        influencer.niche = request.form.get("niche")
        influencer.reach = request.form.get("reach")
        influencer.platform = request.form.get("platform")

        profile_picture = request.files["profile_picture"]
        if profile_picture:
            try:
                filename = secure_filename(profile_picture.filename)
                save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                profile_picture.save(save_path)
                influencer.profile_picture = filename
                db.session.commit()
                flash("Influencer updated successfully!", category="success")
                return redirect(url_for("influencer.dashboard"))
            except Exception as e:
                flash(f"Failed to save profile picture: {str(e)}", category="error")
    return render_template("Influencer/editInfluencer.html", influencer=influencer)


@influencer.route("/deleteInfluencer/<int:influencer_id>", methods=["POST"])
@role_required("Influencer")
@login_required
def deleteInfluencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    if influencer.user_id != current_user.id:
        flash("You are not authorized to delete this profile.", "error")
        return redirect(url_for("influencer.viewInfluencers"))
    for rating in influencer.ratings:
        db.session.delete(rating)

    for transaction in influencer.transactions:
        transaction.influencer_id = None

    db.session.delete(influencer)
    db.session.commit()
    flash("Profile deleted successfully!", category="success")
    return redirect(url_for("influencer.dashboard"))


@influencer.route("/dashboard", methods=["GET", "POST"])
@role_required("Influencer")
@login_required
def dashboard():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    if influencer:
        avg_rating_query = (
            db.session.query(func.avg(Rating.rating).label("average_rating"))
            .filter(Rating.ratee_id == influencer.id)
            .first()
        )
        average_rating = avg_rating_query.average_rating
        if influencer:
            ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
            campaignRequests = campaignRequest.query.filter_by(
                influencer_id=influencer.id
            ).all()
            campaign_requests_with_details = []
            for campaign_request in campaignRequests:
                campaign = Campaign.query.get(campaign_request.campaign_id)
                if campaign:
                    campaign_name = campaign.name
                    campaign_requests_with_details.append(
                        {
                            "campaign_request": campaign_request,
                            "campaign_name": campaign_name,
                        }
                    )
                else:
                    flash("Campaign not found", category="error")

            ad_requests_with_details = []
            for ad_request in ad_requests:
                campaign = Campaign.query.get(ad_request.campaign_id)
                user = User.query.get(campaign.user_id)
                ad_requests_with_details.append(
                    {
                        "ad_request": ad_request,
                        "campaign_name": campaign.name,
                        "user_name": user.name,
                    }
                )

            transactions = Transaction.query.filter_by(
                influencer_id=influencer.id
            ).all()

            # Calculate total earnings
            total_earnings = sum(transaction.amount for transaction in transactions)
            return render_template(
                "Influencer/dashboard.html",
                campaign_requests=campaign_requests_with_details,
                user=current_user,
                influencer=influencer,
                ad_requests=ad_requests_with_details,
                total_earnings=total_earnings,
                average_rating=average_rating,
            )

    return render_template("Influencer/dashboard.html")


# --------------Campaigns-------------------#
@influencer.route("/activeCampaigns", methods=["GET"])
@role_required("Influencer")
@login_required
def activeCampaigns():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    ad_requests = AdRequest.query.filter_by(
        influencer_id=influencer.id, completed=False
    ).all()
    ad_requests_with_details = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        user = User.query.get(campaign.user_id)
        ad_requests_with_details.append(
            {
                "request": ad_request,
                "campaign_name": campaign.name,
                "user_name": user.name,
                "request_type": "Received",
            }
        )

    campaign_requests = campaignRequest.query.filter_by(
        influencer_id=influencer.id, completed=False
    ).all()
    campaign_requests_with_details = []
    for campaign_request in campaign_requests:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        user = User.query.get(campaign.user_id)
        campaign_requests_with_details.append(
            {
                "request": campaign_request,
                "campaign_name": campaign.name,
                "user_name": user.name,
                "request_type": "Sent",
            }
        )
    return render_template(
        "Influencer/activeCampaigns.html",
        user=current_user,
        influencer=influencer,
        ad_requests=ad_requests_with_details,
        campaign_requests=campaign_requests_with_details,
    )


@influencer.route("/viewCampaigns", methods=["GET", "POST"])
@role_required("Influencer")
@login_required
def viewCampaigns():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    if request.method == "POST":
        search_query = request.form.get("search_query")
        campaigns = Campaign.query.filter(
            Campaign.name.ilike(f"%{search_query}%")
        ).all()
    else:
        campaigns = Campaign.query.filter_by(flagged=False).all()
    for campaign in campaigns:
        campaign.is_bookmarked = (
            Bookmark.query.filter_by(
                influencer_id=current_user.id, campaign_id=campaign.id
            ).first()
            is not None
        )
    return render_template(
        "Influencer/viewCampaigns.html", campaigns=campaigns, influencer=influencer
    )


@influencer.route("/viewCampaign/<int:campaign_id>")
@role_required("Influencer")
@login_required
def viewCampaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    return render_template("Influencer/viewCampaign.html", campaign=campaign)


@influencer.route("/search_campaigns", methods=["GET", "POST"])
@login_required
@role_required("Influencer")
def search_campaigns():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        campaigns = Campaign.query.filter(
            Campaign.name.ilike(f"%{search_query}%")
        ).all()
        for campaign in campaigns:
            campaign.is_bookmarked = (
                Bookmark.query.filter_by(
                    influencer_id=current_user.id, campaign_id=campaign.id
                ).first()
                is not None
            )
        return render_template(
            "Influencer/searchResults.html",
            campaigns=campaigns,
            search_query=search_query,
        )
    return render_template("Influencer/viewCampaigns.html")


@influencer.route(
    "/activeCampaigns/<int:ad_request_id>/mark_completed", methods=["POST"]
)
@login_required
@role_required("Influencer")
def mark_completed(ad_request_id):
    request_type = request.form.get("request_type")
    if request_type == "Received":
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        if ad_request:
            ad_request.completed = True
            db.session.commit()
            flash("Ad request completed successfully.", category="success")

    if request_type == "Sent":
        campaign_request = campaignRequest.query.get_or_404(ad_request_id)
        if campaign_request:
            campaign_request.completed = True
            db.session.commit()
            flash("Ad request completed successfully.", category="success")

    return redirect(url_for("influencer.dashboard"))


# ---------------------------Ad Requests---------------------------#
@influencer.route("/view_completed_requests", methods=["GET"])
@role_required("Influencer")
@login_required
def view_completed_requests():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    ad_requests = AdRequest.query.filter_by(
        influencer_id=influencer.id, completed=True
    ).all()
    print(ad_requests)
    ad_requests_with_details = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        user = User.query.get(campaign.user_id)
        ad_requests_with_details.append(
            {
                "request": ad_request,
                "campaign_name": campaign.name,
                "user_name": user.name,
                "request_type": "Received",
            }
        )

    campaign_requests = campaignRequest.query.filter_by(
        influencer_id=influencer.id, completed=True
    ).all()
    campaign_requests_with_details = []
    for campaign_request in campaign_requests:
        campaign = Campaign.query.get(campaign_request.campaign_id)
        user = User.query.get(campaign.user_id)
        campaign_requests_with_details.append(
            {
                "request": campaign_request,
                "campaign_name": campaign.name,
                "user_name": user.name,
                "request_type": "Sent",
            }
        )
    return render_template(
        "Influencer/view_completed_requests.html",
        user=current_user,
        influencer=influencer,
        ad_requests=ad_requests_with_details,
        campaign_requests=campaign_requests_with_details,
    )


@influencer.route("/viewRequest/<int:ad_request_id>", methods=["GET"])
@role_required("Influencer")
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
        "ad_request": ad_request,
        "campaign_name": campaign.name,
        "user_name": user.name,
    }
    negotiations = (
        Negotiation.query.filter_by(
            ad_request_id=ad_request.id, receiver_id=current_user.id
        )
        .order_by(desc(Negotiation.created_at))
        .all()
    )
    latest_nego = (
        Negotiation.query.filter_by(
            ad_request_id=ad_request.id, receiver_id=current_user.id, status="Accepted"
        )
        .order_by(desc(Negotiation.created_at))
        .first()
    )
    latest_pending_nego = (
        Negotiation.query.filter_by(
            ad_request_id=ad_request.id, receiver_id=current_user.id, status="Pending"
        )
        .order_by(desc(Negotiation.created_at))
        .first()
    )
    print(latest_pending_nego)
    latest_price = (
        latest_nego.offer_amount if latest_nego else ad_request.payment_amount
    )

    return render_template(
        "Influencer/viewRequest.html",
        ad_request_details=ad_request_with_details,
        negotiations=negotiations,
        latest_price=latest_price,
        latest_pending_nego=latest_pending_nego,
    )


@influencer.route(
    "/edit_campaign_request/<int:campaign_request_id>", methods=["GET", "POST"]
)
@role_required("Influencer")
@login_required
def edit_campaign_request(campaign_request_id):
    campaign_request = campaignRequest.query.get_or_404(campaign_request_id)
    if request.method == "POST":
        campaign_request.messages = request.form.get("messages")
        campaign_request.requirements = request.form.get("requirements")
        campaign_request.payment_amount = request.form.get("payment_amount")

        db.session.commit()
        flash("Campaign request updated successfully.", category="success")
        return redirect(url_for("influencer.dashboard"))
    return render_template(
        "Influencer/edit_sent_request.html", campaign_request=campaign_request
    )


@influencer.route(
    "/delete_campaign_request/<int:campaign_request_id>", methods=["POST"]
)
@role_required("Influencer")
@login_required
def delete_campaign_request(campaign_request_id):
    campaign_request = campaignRequest.query.get_or_404(campaign_request_id)
    db.session.delete(campaign_request)
    db.session.commit()
    flash("Campaign request deleted successfully.", category="success")
    return redirect(url_for("influencer.dashboard"))


@influencer.route("/ad_request/<int:ad_request_id>/accept", methods=["POST"])
@role_required("Influencer")
@login_required
def accept_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)

    payment_amount = request.form.get("payment_amount")
    ad_request.status = "Accepted"
    ad_request.payment_amount = payment_amount
    db.session.commit()
    flash("Ad request accepted successfully.", category="success")
    return redirect(url_for("influencer.dashboard"))


@influencer.route("/ad_request/<int:ad_request_id>/reject", methods=["POST"])
@role_required("Influencer")
@login_required
def reject_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    ad_request.status = "Rejected"
    db.session.commit()
    flash("Ad request rejected successfully.", category="success")
    return redirect(url_for("influencer.dashboard"))


@influencer.route("create_ad_request/<int:campaign_id>", methods=["GET", "POST"])
@role_required("Influencer")
@login_required
def create_ad_request(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()

    if not campaign:
        flash("Campaign not found", "error")
        return redirect(url_for("sponsor.dashboard"))

    if request.method == "POST":
        messages = request.form.get("messages")
        requirements = request.form.get("requirements")
        payment_amount = request.form.get("payment_amount")

        if not influencer:
            flash("Influencer name is required", "error")
            return render_template(
                "Influencer/create_ad_request.html", campaign=campaign
            )

        ad_request = campaignRequest(
            campaign_id=campaign.id,
            influencer_id=influencer.id,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
        )

        db.session.add(ad_request)
        db.session.commit()

        flash("Ad request created successfully", category="success")
        return redirect(url_for("influencer.dashboard"))
    return render_template("Influencer/create_ad_request.html", campaign=campaign)


# ----------------------Bookmark Campaign----------------------#
@influencer.route("/bookmark_campaign/<int:campaign_id>", methods=["POST"])
@role_required("Influencer")
@login_required
def bookmark_campaign(campaign_id):
    if request.method == "POST":
        # Check if the campaign is already bookmarked
        bookmark = Bookmark.query.filter_by(
            influencer_id=current_user.id, campaign_id=campaign_id
        ).first()
        if bookmark:
            # If already bookmarked, remove the bookmark
            db.session.delete(bookmark)
            db.session.commit()
        else:
            # If not bookmarked, create a new bookmark entry
            new_bookmark = Bookmark(
                influencer_id=current_user.id, campaign_id=campaign_id
            )
            db.session.add(new_bookmark)
            db.session.commit()
        return redirect(url_for("influencer.viewCampaigns", campaign_id=campaign_id))


@influencer.route("/view_bookmarks")
@role_required("Influencer")
@login_required
def view_bookmarks():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    campaigns = Campaign.query.all()
    for campaign in campaigns:
        campaign.is_bookmarked = (
            Bookmark.query.filter_by(
                influencer_id=current_user.id, campaign_id=campaign.id
            ).first()
            is not None
        )
    influencer_bookmarks = Bookmark.query.filter_by(influencer_id=current_user.id).all()
    bookmarked_campaigns = [
        Campaign.query.get(bookmark.campaign_id) for bookmark in influencer_bookmarks
    ]

    return render_template(
        "Influencer/Bookmarks.html",
        bookmarked_campaigns=bookmarked_campaigns,
        campaigns=campaigns,
        influencer=influencer,
    )


# -----------------------Ratings-------------------------#
@influencer.route("/view_ratings")
@role_required("Influencer")
@login_required
def view_ratings():
    influencers = current_user.influencers
    influencer = influencers[0] if influencers else None
    ratings = Rating.query.filter_by(ratee_id=influencer.id).all()
    ratings_with_details = []
    for rating in ratings:
        sponsor = User.query.get(rating.rater_id)
        sponsor_name = sponsor.name
        ratings_with_details.append(
            {
                "rating": rating,
                "sponsor_name": sponsor_name,
            }
        )
    return render_template("Influencer/view_ratings.html", ratings=ratings_with_details)


@influencer.route("make_ad_offer/<int:ad_request_id>", methods=["POST", "GET"])
@role_required("Influencer")
@login_required
def make_ad_offer(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    campaign = Campaign.query.get(ad_request.campaign_id)
    sponsor = User.query.get(campaign.user_id)
    sender_id = sponsor.id
    if request.method == "POST":
        offer_amount = request.form.get("offer_amount")
        negotiation = Negotiation(
            campaign_id=campaign.id,
            ad_request_id=ad_request_id,
            offer_amount=offer_amount,
            sender_id=sender_id,
            receiver_id=current_user.id,
        )
        db.session.add(negotiation)
        db.session.commit()
        flash("Offer created successfully", "success")
        return redirect(url_for("influencer.dashboard"))
    return render_template("Influencer/dashboard.html", ad_request=ad_request)
