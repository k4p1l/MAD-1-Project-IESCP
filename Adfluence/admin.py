from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy.sql import func, extract

from . import db  # means from __init__.py import db
from .models import (
    User,
    Influencer,
    AdRequest,
    Campaign,
    campaignRequest,
    Bookmark,
    Transaction,
    Rating,
)
from .views import role_required

admin = Blueprint("admin", __name__)


@admin.route("/dashboard")
@role_required("Admin")
@login_required
def dashboard():
    user_count = User.query.count()
    influencer_count = Influencer.query.count()
    sponsor_count = user_count - influencer_count
    campaign_count = Campaign.query.count()
    transaction_count = Transaction.query.count()
    total_transaction_amount = (
        db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    )
    average_transaction_amount = (
        db.session.query(db.func.avg(Transaction.amount)).scalar() or 0
    )
    ad_request_count = AdRequest.query.count()
    average_influencer_balance = (
        db.session.query(db.func.avg(Influencer.bank_account_balance)).scalar() or 0
    )
    average_rating = db.session.query(db.func.avg(Rating.rating)).scalar() or 0

    campaigns_by_status = (
        db.session.query(Campaign.status, db.func.count(Campaign.id))
        .group_by(Campaign.status)
        .all()
    )
    labels_campaign_by_status = [campaign[0] for campaign in campaigns_by_status]
    values_campaign_by_status = [campaign[1] for campaign in campaigns_by_status]

    return render_template(
        "Admin/dashboard.html",
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
        values_campaign_by_status=values_campaign_by_status,
    )


@admin.route("/influencer_stats")
@role_required("Admin")
@login_required
def influencer_stats():
    influencer_count = Influencer.query.count()
    most_used_platform = (
        db.session.query(Influencer.platform, func.count(Influencer.platform))
        .group_by(Influencer.platform)
        .order_by(func.count(Influencer.platform).desc())
        .first()
    )
    most_populated_niche = (
        db.session.query(Influencer.niche, func.count(Influencer.niche))
        .group_by(Influencer.niche)
        .order_by(func.count(Influencer.niche).desc())
        .first()
    )
    average_influencer_balance = (
        db.session.query(db.func.avg(Influencer.bank_account_balance)).scalar() or 0
    )
    influencers_by_niche = (
        db.session.query(Influencer.niche, func.count(Influencer.niche))
        .group_by(Influencer.niche)
        .all()
    )
    influencers_by_niche_labels = [influencer[0] for influencer in influencers_by_niche]
    influencers_by_niche_values = [influencer[1] for influencer in influencers_by_niche]

    influencers_by_platform = (
        db.session.query(Influencer.platform, func.count(Influencer.platform))
        .group_by(Influencer.platform)
        .all()
    )
    influencers_by_platform_labels = [
        influencer[0] for influencer in influencers_by_platform
    ]
    influencers_by_platform_values = [
        influencer[1] for influencer in influencers_by_platform
    ]

    average_influencer_reach = (
        db.session.query(db.func.avg(Influencer.reach)).scalar() or 0
    )

    return render_template(
        "Admin/influencer_stats.html",
        influencer_count=influencer_count,
        most_used_platform=most_used_platform,
        most_populated_niche=most_populated_niche,
        average_influencer_balance=average_influencer_balance,
        influencers_by_niche_labels=influencers_by_niche_labels,
        influencers_by_niche_values=influencers_by_niche_values,
        influencers_by_platform=influencers_by_platform,
        average_influencer_reach=average_influencer_reach,
        influencers_by_platform_labels=influencers_by_platform_labels,
        influencers_by_platform_values=influencers_by_platform_values,
    )


@admin.route("/sponsor_stats")
@role_required("Admin")
@login_required
def sponsor_stats():
    influencer_count = Influencer.query.count()
    user_count = User.query.count()

    sponsor_count = user_count - influencer_count
    most_populated_niche = (
        db.session.query(User.niche, func.count(User.niche))
        .filter(User.role == "Sponsor")
        .group_by(User.niche)
        .order_by(func.count(User.niche).desc())
        .first()
    )
    sponsor_by_niche = (
        db.session.query(User.niche, func.count(User.niche))
        .filter(User.role == "Sponsor")
        .group_by(User.niche)
        .all()
    )
    sponsor_by_niche_labels = [sponsor[0] for sponsor in sponsor_by_niche]
    sponsor_by_niche_values = [sponsor[1] for sponsor in sponsor_by_niche]
    transaction_count = Transaction.query.count()
    total_transaction_amount = (
        db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    )
    average_transaction_amount = (
        db.session.query(db.func.avg(Transaction.amount)).scalar() or 0
    )
    transaction_by_request_type = (
        db.session.query(Transaction.request_type, func.count(Transaction.request_type))
        .group_by(Transaction.request_type)
        .all()
    )
    transaction_by_request_type_labels = [
        transaction[0] for transaction in transaction_by_request_type
    ]
    transaction_by_request_type_values = [
        transaction[1] for transaction in transaction_by_request_type
    ]

    return render_template(
        "Admin/sponsor_stats.html",
        most_populated_niche=most_populated_niche,
        sponsor_count=sponsor_count,
        transaction_count=transaction_count,
        total_transaction_amount=total_transaction_amount,
        average_transaction_amount=average_transaction_amount,
        transaction_by_request_type=transaction_by_request_type,
        transaction_by_request_type_labels=transaction_by_request_type_labels,
        transaction_by_request_type_values=transaction_by_request_type_values,
        sponsor_by_niche=sponsor_by_niche,
        sponsor_by_niche_labels=sponsor_by_niche_labels,
        sponsor_by_niche_values=sponsor_by_niche_values,
    )


@admin.route("/campaign_stats")
@role_required("Admin")
@login_required
def campaign_stats():
    campaign_count = Campaign.query.count()
    campaigns_by_visibility = (
        db.session.query(Campaign.visibility, db.func.count(Campaign.id))
        .group_by(Campaign.visibility)
        .all()
    )

    campaign_by_visibility_labels = [
        campaign[0] for campaign in campaigns_by_visibility
    ]
    campaign_by_visibility_values = [
        campaign[1] for campaign in campaigns_by_visibility
    ]

    most_populated_niches = (
        db.session.query(Campaign.niche, func.count(Campaign.niche))
        .group_by(Campaign.niche)
        .order_by(func.count(Campaign.niche).desc())
        .limit(2)
        .all()
    )
    # Extracting the first and second values
    if len(most_populated_niches) > 1:
        first_most_populated_niche = most_populated_niches[0]
        second_most_populated_niche = most_populated_niches[1]
    elif len(most_populated_niches) == 1:
        first_most_populated_niche = most_populated_niches[0]
        second_most_populated_niche = None
    else:
        first_most_populated_niche = None
        second_most_populated_niche = None
    campaigns_by_niche = (
        db.session.query(Campaign.niche, db.func.count(Campaign.id))
        .group_by(Campaign.niche)
        .all()
    )

    campaign_by_niche_labels = [campaign[0] for campaign in campaigns_by_niche]
    campaign_by_niche_values = [campaign[1] for campaign in campaigns_by_niche]

    # Fetch ad_requests data
    ad_requests_data = (
        db.session.query(AdRequest.status, func.count(AdRequest.id))
        .group_by(AdRequest.status)
        .all()
    )

    # Fetch campaign_requests data
    campaign_requests_data = (
        db.session.query(campaignRequest.status, func.count(campaignRequest.id))
        .group_by(campaignRequest.status)
        .all()
    )

    # Combine both data sets
    combined_requests_data = {}
    for status, count in ad_requests_data + campaign_requests_data:
        if status in combined_requests_data:
            combined_requests_data[status] += count
        else:
            combined_requests_data[status] = count

    ads_by_status_labels = list(combined_requests_data.keys())
    ads_by_status_values = list(combined_requests_data.values())

    ad_requests_data_1 = (
        db.session.query(AdRequest.payment_done, func.count(AdRequest.id))
        .group_by(AdRequest.payment_done)
        .all()
    )

    campaign_requests_data_1 = (
        db.session.query(campaignRequest.payment_done, func.count(campaignRequest.id))
        .group_by(campaignRequest.payment_done)
        .all()
    )

    combined_requests_data_1 = {}
    for status, count in ad_requests_data_1 + campaign_requests_data_1:
        if status in combined_requests_data_1:
            combined_requests_data_1[status] += count
        else:
            combined_requests_data_1[status] = count
    status_mapping = {False: "Payment Pending", True: "Payment Done"}
    renamed_combined_requests_data_1 = {
        status_mapping[status]: count
        for status, count in combined_requests_data_1.items()
    }

    ads_by_status_labels_1 = list(renamed_combined_requests_data_1.keys())
    ads_by_status_values_1 = list(renamed_combined_requests_data_1.values())

    average_campaign_budget = (
        db.session.query(func.round(func.avg(Campaign.budget)), 2).scalar() or 0
    )
    ad_request_count = db.session.query(func.count(AdRequest.id)).scalar() or 0
    campaign_request_count = (
        db.session.query(func.count(campaignRequest.id)).scalar() or 0
    )
    total_request_count = ad_request_count + campaign_request_count
    total_budget = db.session.query(func.sum(Campaign.budget)).scalar() or 0
    bookmark_count = Bookmark.query.count()
    most_popular_influencer_niche = (
        db.session.query(Influencer.niche, func.count(Influencer.niche))
        .group_by(Influencer.niche)
        .order_by(func.count(Influencer.niche).desc())
        .first()
    )
    return render_template(
        "Admin/campaign_stats.html",
        total_request_count=total_request_count,
        total_budget=total_budget,
        first_most_populated_niche=first_most_populated_niche,
        second_most_populated_niche=second_most_populated_niche,
        most_popular_influencer_niche=most_popular_influencer_niche,
        campaign_count=campaign_count,
        bookmark_count=bookmark_count,
        campaigns_by_visibility=campaigns_by_visibility,
        campaigns_by_niche=campaigns_by_niche,
        average_campaign_budget=average_campaign_budget,
        ads_by_status_labels=ads_by_status_labels,
        ads_by_status_values=ads_by_status_values,
        campaign_by_visibility_labels=campaign_by_visibility_labels,
        campaign_by_visibility_values=campaign_by_visibility_values,
        campaign_by_niche_labels=campaign_by_niche_labels,
        campaign_by_niche_values=campaign_by_niche_values,
        ads_by_payment_labels=ads_by_status_labels_1,
        ads_by_payment_values=ads_by_status_values_1,
    )


@admin.route("view_campaigns", methods=["GET", "POST"])
@role_required("Admin")
@login_required
def view_campaigns():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        campaigns = Campaign.query.filter(
            Campaign.name.ilike(f"%{search_query}%")
        ).all()
    else:
        campaigns = Campaign.query.all()
    return render_template("Admin/view_campaigns.html", campaigns=campaigns)


@admin.route("/flag_campaign/<int:campaign_id>", methods=["POST"])
@role_required("Admin")
@login_required
def flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = True
    db.session.commit()
    flash("Campaign flagged!", category="success")
    return redirect(url_for("admin.view_campaigns"))


@admin.route("/unflag_campaign/<int:campaign_id>", methods=["POST"])
@role_required("Admin")
@login_required
def unflag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.flagged = False
    db.session.commit()
    flash("Campaign unflagged!", category="success")
    return redirect(url_for("admin.view_flagged_campaigns"))


@admin.route("/delete_campaign/<int:campaign_id>", methods=["POST"])
@role_required("Admin")
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign deleted!", category="success")
    return redirect(url_for("admin.view_flagged_campaigns"))


@admin.route("/view_flagged_campaigns")
@role_required("Admin")
@login_required
def view_flagged_campaigns():
    campaigns = Campaign.query.filter_by(flagged=True).all()
    return render_template("Admin/view_flagged_campaigns.html", campaigns=campaigns)


@admin.route("/view_influencers", methods=["GET", "POST"])
@role_required("Admin")
@login_required
def view_influencers():
    # Get parameters from the request
    reach = request.args.get("reach")
    niche = request.args.get("niche")

    # Base query
    query = Influencer.query

    # Apply filters if provided
    if reach:
        query = query.filter(Influencer.reach >= int(reach))
    if niche:
        query = query.filter(Influencer.niche == niche)

    # Execute the query
    filtered_influencers = query.all()
    return render_template(
        "Admin/view_influencers.html", influencers=filtered_influencers
    )


@admin.route("/view_all_influencers")
@role_required("Admin")
@login_required
def view_all_influencers():
    influencers = Influencer.query.all()
    return render_template("Admin/view_influencers.html", influencers=influencers)


@admin.route("/flag_influencer/<int:influencer_id>", methods=["POST"])
@role_required("Admin")
@login_required
def flag_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    influencer.flagged = True
    db.session.commit()
    flash("Influencer flagged!", category="success")
    return redirect(url_for("admin.view_influencers"))


@admin.route("/unflag_influencer/<int:influencer_id>", methods=["POST"])
@role_required("Admin")
@login_required
def unflag_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    influencer.flagged = False
    db.session.commit()
    flash("Influencer Reinstated!", category="success")
    return redirect(url_for("admin.view_flagged_influencers"))


@admin.route("/delete_influencer/<int:influencer_id>", methods=["POST"])
@role_required("Admin")
@login_required
def delete_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)

    with db.session.no_autoflush:
        for rating in influencer.ratings:
            db.session.delete(rating)

        for transaction in influencer.transactions:
            transaction.influencer_id = None
            db.session.delete(transaction)

        for adrequest in influencer.adrequests:
            if adrequest:
                db.session.delete(adrequest)

        for campaignrequest in influencer.campaignrequests:
            if campaignrequest:
                db.session.delete(campaignrequest)

        user = User.query.get(influencer.user_id)
        db.session.delete(user)
        db.session.delete(influencer)

    db.session.commit()
    flash("Influencer deleted!", category="success")
    return redirect(url_for("admin.view_influencers"))


@admin.route("/view_flagged_influencers")
@role_required("Admin")
@login_required
def view_flagged_influencers():
    influencers = Influencer.query.filter_by(flagged=True).all()
    return render_template(
        "Admin/view_flagged_influencers.html", influencers=influencers
    )


@admin.route("/view_sponsors", methods=["GET", "POST"])
@role_required("Admin")
@login_required
def view_sponsors():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        base_query = User.query.filter_by(role="Sponsor")
        sponsors = base_query.filter(User.name.ilike(f"%{search_query}%")).all()
    else:
        sponsors = User.query.filter_by(role="Sponsor").all()
        print(sponsors)
    return render_template("Admin/view_sponsors.html", sponsors=sponsors)


@admin.route("/view_flagged_sponsors", methods=["GET", "POST"])
@role_required("Admin")
@login_required
def view_flagged_sponsors():
    sponsors = User.query.filter_by(flagged=True).all()
    return render_template("Admin/view_flagged_sponsors.html", sponsors=sponsors)


@admin.route("flag_sponsor/<int:user_id>", methods=["POST"])
@role_required("Admin")
@login_required
def flag_sponsor(user_id):
    user = User.query.get_or_404(user_id)
    user.flagged = True
    db.session.commit()
    flash("Sponsor flagged!", category="success")
    return redirect(url_for("admin.view_sponsors"))


@admin.route("unflag_sponsor/<int:user_id>", methods=["POST"])
@role_required("Admin")
@login_required
def unflag_sponsor(user_id):
    user = User.query.get_or_404(user_id)
    user.flagged = False
    db.session.commit()
    flash("Sponsor reinstated!", category="success")
    return redirect(url_for("admin.view_flagged_sponsors"))


@admin.route("delete_sponsor/<int:user_id>", methods=["POST"])
@role_required("Admin")
@login_required
def delete_sponsor(user_id):
    user = User.query.get_or_404(user_id)
    for campaign in user.campaigns:
        if campaign:
            db.session.delete(campaign)
    for rating in user.ratings:
        if rating:
            db.session.delete(rating)
    for transaction in user.transactions:
        if transaction:
            transaction.user_id = None

    db.session.delete(user)
    db.session.commit()
    flash("Sponsor deleted!", category="success")
    return redirect(url_for("admin.view_sponsors"))


# Fetch transactions and group by date
@admin.route("/transaction_stats")
@role_required("Admin")
@login_required
def transaction_stats():
    transactions = (
        db.session.query(
            extract("year", Transaction.date).label("year"),
            extract("month", Transaction.date).label("month"),
            func.count(Transaction.id).label("count"),
        )
        .group_by(extract("year", Transaction.date), extract("month", Transaction.date))
        .all()
    )
    month_labels = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    labels = []
    transaction_counts = []

    for record in transactions:
        year = int(record.year)
        month = int(record.month)
        labels.append(f"{month_labels[month - 1]} {year}")
        transaction_counts.append(record.count)
    transaction_count = Transaction.query.count()
    total_transaction_amount = (
        db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    )
    average_transaction_amount = (
        db.session.query(db.func.avg(Transaction.amount)).scalar() or 0
    )
    return render_template(
        "Admin/transactions_stats.html",
        labels=labels,
        transaction_counts=transaction_counts,
        transaction_count=transaction_count,
        total_transaction_amount=total_transaction_amount,
        average_transaction_amount=average_transaction_amount,
    )
