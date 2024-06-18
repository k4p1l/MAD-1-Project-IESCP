from flask import Flask
from .models import db, Campaign, User, AdRequest, Influencer, Rating, campaignRequest
from flask_restful import Resource, marshal_with, fields, reqparse
from datetime import datetime
import json

campaign_parser = reqparse.RequestParser()
campaign_parser.add_argument("name", type=str, required=True, help="Name is required")
campaign_parser.add_argument(
    "description", type=str, required=True, help="Description is required"
)
campaign_parser.add_argument(
    "start_date", type=str, required=True, help="Start date is required"
)
campaign_parser.add_argument(
    "end_date", type=str, required=True, help="End date is required"
)
campaign_parser.add_argument(
    "budget", type=int, required=True, help="Budget is required"
)
campaign_parser.add_argument(
    "visibility",
    type=str,
    required=True,
    choices=("public", "private"),
    help="Visibility must be public or private",
)
campaign_parser.add_argument(
    "goals", type=str, required=True, help="Goals are required"
)
campaign_parser.add_argument("niche", type=str, required=True, help="Niche is required")
campaign_parser.add_argument(
    "user_id", type=int, required=True, help="User ID is required"
)

campaign_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "start_date": fields.String(
        attribute=lambda x: x.start_date.strftime("%Y-%m-%d")
    ),  # The attribute parameter in fields.String specifies how to extract the value from the object (x) being serialized. Here, it's a lambda function that formats the start_date attribute of x into a string.
    "end_date": fields.String(attribute=lambda x: x.end_date.strftime("%Y-%m-%d")),
    "budget": fields.Integer,
    "visibility": fields.String,
    "goals": fields.String,
    "niche": fields.String,
    "status": fields.String,
    "flagged": fields.Boolean,
    "user_id": fields.Integer,
}

adrequest_parser = reqparse.RequestParser()
adrequest_parser.add_argument(
    "campaign_id", type=int, required=True, help="Campaign ID is required"
)
adrequest_parser.add_argument(
    "influencer_id", type=int, required=True, help="Influencer ID is required"
)
adrequest_parser.add_argument(
    "messages", type=str, required=True, help="Messages are required"
)
adrequest_parser.add_argument(
    "requirements", type=str, required=True, help="Requirements are required"
)
adrequest_parser.add_argument(
    "payment_amount", type=float, required=True, help="Payment amount is required"
)
adrequest_parser.add_argument(
    "status", type=str, required=True, help="Status is required"
)

adrequest_fields = {
    "id": fields.Integer,
    "campaign_id": fields.Integer,
    "influencer_id": fields.Integer,
    "messages": fields.String,
    "requirements": fields.String,
    "payment_amount": fields.Float,
    "status": fields.String,
    "completed": fields.Boolean,
    "completion_confirmed": fields.Boolean,
    "payment_done": fields.Boolean,
    "rating_done": fields.Boolean,
}

campaignrequest_parser = reqparse.RequestParser()
campaignrequest_parser.add_argument(
    "campaign_id", type=int, required=True, help="Campaign ID is required"
)
campaignrequest_parser.add_argument(
    "influencer_id", type=int, required=True, help="Influencer ID is required"
)
campaignrequest_parser.add_argument(
    "messages", type=str, required=True, help="Messages are required"
)
campaignrequest_parser.add_argument(
    "requirements", type=str, required=True, help="Requirements are required"
)
campaignrequest_parser.add_argument(
    "payment_amount", type=float, required=True, help="Payment amount is required"
)
campaignrequest_parser.add_argument(
    "status", type=str, required=True, help="Status is required"
)

campaignrequest_fields = {
    "id": fields.Integer,
    "campaign_id": fields.Integer,
    "influencer_id": fields.Integer,
    "messages": fields.String,
    "requirements": fields.String,
    "payment_amount": fields.Float,
    "status": fields.String,
    "completed": fields.Boolean,
    "completion_confirmed": fields.Boolean,
    "payment_done": fields.Boolean,
    "rating_done": fields.Boolean,
}

user_parser = reqparse.RequestParser()
user_parser.add_argument("email", type=str, required=True, help="Email is required")
user_parser.add_argument("name", type=str, required=True, help="Name is required")
user_parser.add_argument("role", type=str, required=True, help="Role is required")
user_parser.add_argument("niche", type=str, required=True, help="Niche is required")
user_parser.add_argument(
    "password", type=str, required=True, help="Password is required"
)

user_fields = {
    "id": fields.Integer,
    "email": fields.String,
    "name": fields.String,
    "role": fields.String,
    "niche": fields.String,
    "password": fields.String,
}

Influencer_parser = reqparse.RequestParser()
Influencer_parser.add_argument("name", type=str, required=True, help="Name is required")
Influencer_parser.add_argument(
    "email", type=str, required=True, help="Email is required"
)
Influencer_parser.add_argument(
    "profile_picture", type=str, required=True, help="Profile picture is required"
)
Influencer_parser.add_argument(
    "niche", type=str, required=True, help="Niche is required"
)
Influencer_parser.add_argument(
    "reach", type=int, required=True, help="Reach is required"
)
Influencer_parser.add_argument(
    "platform", type=str, required=True, help="Platform is required"
)
Influencer_parser.add_argument("bank_account_balance", type=float, default=0.0)
Influencer_parser.add_argument("flagged", type=bool, default=False)

Influencer_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String,
    "profile_picture": fields.String,
    "niche": fields.String,
    "reach": fields.Integer,
    "user_id": fields.Integer,
    "platform": fields.String,
    "bank_account_balance": fields.Float,
    "flagged": fields.Boolean,
}

rating_parser = reqparse.RequestParser()
rating_parser.add_argument(
    "influencer_id", type=int, required=True, help="Influencer ID is required"
)
rating_parser.add_argument("rating", type=int, required=True, help="Rating is required")
rating_parser.add_argument("review", type=str, required=True, help="Review is required")
rating_parser.add_argument(
    "ratee_id", type=int, required=True, help="Review is required"
)
rating_parser.add_argument(
    "rater_id", type=int, required=True, help="Review is required"
)
rating_parser.add_argument("date", type=str, required=True, help="Review is required")

rating_fields = {
    "id": fields.Integer,
    "influencer_id": fields.Integer,
    "rating": fields.Integer,
    "review": fields.String,
    "ratee_id": fields.Integer,
    "rater_id": fields.Integer,
    "date": fields.String(attribute=lambda x: x.date.strftime("%Y-%m-%d")),
}


# ------------User API---------------------#
class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, id=None):
        if id:
            user = User.query.get_or_404(id)
            return user
        else:
            users = User.query.all()
            return users

    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        user = User(
            email=args["email"],
            name=args["name"],
            role=args["role"],
            niche=args["niche"],
            password=args["password"],
        )
        db.session.add(user)
        db.session.commit()
        return user

    @marshal_with(user_fields)
    def put(self, id):
        args = user_parser.parse_args()
        user = User.query.get_or_404(id)
        if "email" in args:
            user.email = args["email"]
        if "name" in args:
            user.name = args["name"]
        if "role" in args:
            user.role = args["role"]
        if "niche" in args:
            user.niche = args["niche"]
        if "password" in args:
            user.password = args["password"]
        db.session.commit()
        return user

    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return "", 204


# ------------Influencer API---------------------#
class InfluencerAPI(Resource):
    @marshal_with(Influencer_fields)
    def get(self, id=None):
        if id:
            influencer = Influencer.query.get_or_404(id)
            return influencer
        else:
            influencers = Influencer.query.all()
            return influencers

    @marshal_with(Influencer_fields)
    def post(self):
        args = Influencer_parser.parse_args()
        influencer = Influencer(
            name=args["name"],
            email=args["email"],
            profile_picture=args["profile_picture"],
            niche=args["niche"],
            reach=args["reach"],
            platform=args["platform"],
            bank_account_balance=args.get("bank_account_balance", 0.0),
            flagged=args.get("flagged", False),
        )
        db.session.add(influencer)
        db.session.commit()
        return influencer

    @marshal_with(Influencer_fields)
    def put(self, id):
        args = Influencer_parser.parse_args()
        influencer = Influencer.query.get_or_404(id)
        if "name" in args:
            influencer.name = args["name"]
        if "email" in args:
            influencer.email = args["email"]
        if "profile_picture" in args:
            influencer.profile_picture = args["profile_picture"]
        if "niche" in args:
            influencer.niche = args["niche"]
        if "reach" in args:
            influencer.reach = args["reach"]
        if "platform" in args:
            influencer.platform = args["platform"]
        if "bank_account_balance" in args:
            influencer.bank_account_balance = args.get("bank_account_balance", 0.0)
        if "flagged" in args:
            influencer.flagged = args.get("flagged", False)
        db.session.commit()
        return influencer

    def delete(self, id):
        influencer = Influencer.query.get_or_404(id)
        db.session.delete(influencer)
        db.session.commit()
        return "", 204


# ------------Campaign API---------------------#
class CampaignAPI(Resource):
    @marshal_with(campaign_fields)
    def get(self, id=None):
        if id:
            campaign = Campaign.query.get_or_404(id)
            return campaign
        else:
            campaigns = Campaign.query.all()
            return campaigns

    @marshal_with(campaign_fields)
    def post(self):
        args = campaign_parser.parse_args()

        # Convert start_date and end_date strings to datetime objects
        start_date = datetime.strptime(args["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(args["end_date"], "%Y-%m-%d").date()
        campaign = Campaign(
            name=args["name"],
            description=args["description"],
            start_date=start_date,
            end_date=end_date,
            budget=args["budget"],
            visibility=args["visibility"],
            goals=args["goals"],
            niche=args["niche"],
            user_id=args["user_id"],
        )
        db.session.add(campaign)
        db.session.commit()
        return campaign, 201

    @marshal_with(campaign_fields)
    def put(self, id):
        args = campaign_parser.parse_args()
        campaign = Campaign.query.get_or_404(id)

        if "name" in args:
            campaign.name = args["name"]
        if "description" in args:
            campaign.description = args["description"]
        if "start_date" in args:
            start_date = datetime.strptime(args["start_date"], "%Y-%m-%d").date()
            campaign.start_date = start_date
        if "end_date" in args:
            end_date = datetime.strptime(args["end_date"], "%Y-%m-%d").date()
            campaign.end_date = end_date
        if "budget" in args:
            campaign.budget = args["budget"]
        if "visibility" in args:
            campaign.visibility = args["visibility"]
        if "goals" in args:
            campaign.goals = args["goals"]
        if "niche" in args:
            campaign.niche = args["niche"]
        if "status" in args:
            campaign.status = args["status"]
        if "flagged" in args:
            campaign.flagged = args["flagged"]
        if "user_id" in args:
            campaign.user_id = args["user_id"]
        db.session.commit()
        return campaign, 200

    def delete(self, id):
        campaign = Campaign.query.get_or_404(id)
        db.session.delete(campaign)
        db.session.commit()
        return "", 204


# ------------AdRequest API---------------------#
class AdRequestAPI(Resource):
    @marshal_with(adrequest_fields)
    def get(self, id=None):
        if id:
            ad_request = AdRequest.query.get_or_404(id)
            return ad_request
        else:
            ad_requests = AdRequest.query.all()
            return ad_requests

    @marshal_with(adrequest_fields)
    def post(self):
        args = adrequest_parser.parse_args()
        ad_request = AdRequest(
            campaign_id=args["campaign_id"],
            influencer_id=args["influencer_id"],
            messages=args["messages"],
            requirements=args["requirements"],
            payment_amount=args["payment_amount"],
            status=args["status"],
        )
        db.session.add(ad_request)
        db.session.commit()
        return ad_request, 201

    @marshal_with(adrequest_fields)
    def put(self, id):
        args = adrequest_parser.parse_args()
        ad_request = AdRequest.query.get_or_404(id)

        if "campaign_id" in args:
            ad_request.campaign_id = args["campaign_id"]
        if "influencer_id" in args:
            ad_request.influencer_id = args["influencer_id"]
        if "messages" in args:
            ad_request.messages = args["messages"]
        if "requirements" in args:
            ad_request.requirements = args["requirements"]
        if "payment_amount" in args:
            ad_request.payment_amount = args["payment_amount"]
        if "status" in args:
            ad_request.status = args["status"]
        if "completed" in args:
            ad_request.completed = args["completed"]
        if "completion_confirmed" in args:
            ad_request.completion_confirmed = args["completion_confirmed"]
        if "payment_done" in args:
            ad_request.payment_done = args["payment_done"]
        if "rating_done" in args:
            ad_request.rating_done = args["rating_done"]
        db.session.commit()
        return ad_request, 200

    def delete(self, id):
        ad_request = AdRequest.query.get_or_404(id)
        db.session.delete(ad_request)
        db.session.commit()
        return "", 204


# ------------Campaign Request API---------------------#
class CampaignRequestAPI(Resource):
    @marshal_with(campaignrequest_fields)
    def get(self, id=None):
        if id:
            campaign_request = campaignRequest.query.get_or_404(id)
            return campaign_request
        else:
            campaign_request = campaignRequest.query.all()
            return campaign_request

    @marshal_with(campaignrequest_fields)
    def post(self):
        args = campaignrequest_parser.parse_args()
        campaign_request = campaignRequest(
            influencer_id=args["influencer_id"],
            campaign_id=args["campaign_id"],
            messages=args["messages"],
            requirements=args["requirements"],
            payment_amount=args["payment_amount"],
            status=args["status"],
        )
        db.session.add(campaign_request)
        db.session.commit()
        return campaign_request, 201

    @marshal_with(campaignrequest_fields)
    def put(self, id):
        args = campaignrequest_parser.parse_args()
        campaign_request = campaignRequest.query.get_or_404(id)

        if "campaign_id" in args:
            campaign_request.campaign_id = args["campaign_id"]
        if "influencer_id" in args:
            campaign_request.influencer_id = args["influencer_id"]
        if "messages" in args:
            campaign_request.messages = args["messages"]
        if "requirements" in args:
            campaign_request.requirements = args["requirements"]
        if "payment_amount" in args:
            campaign_request.payment_amount = args["payment_amount"]
        if "status" in args:
            campaign_request.status = args["status"]
        if "completed" in args:
            campaign_request.completed = args["completed"]
        if "completion_confirmed" in args:
            campaign_request.completion_confirmed = args["completion_confirmed"]
        if "payment_done" in args:
            campaign_request.payment_done = args["payment_done"]
        if "rating_done" in args:
            campaign_request.rating_done = args["rating_done"]

        db.session.commit()
        return campaign_request, 200

    def delete(self, id):
        campaign_request = campaignRequest.query.get_or_404(id)
        db.session.delete(campaign_request)
        db.session.commit()
        return "", 204


# ------------Rating API---------------------#
class RatingAPI(Resource):
    @marshal_with(rating_fields)
    def get(self, id=None):
        if id:
            rating = Rating.query.get_or_404(id)
            return rating
        else:
            rating = Rating.query.all()
            return rating

    @marshal_with(rating_fields)
    def post(self):
        args = rating_parser.parse_args()
        rating = Rating(
            campaign_id=args["campaign_id"],
            rating=args["rating"],
            review=args["review"],
            ratee_id=args["ratee_id"],
            rater_id=args["rater_id"],
            date=args["date"],
        )
        db.session.add(rating)
        db.session.commit()
        return rating, 201

    @marshal_with(rating_fields)
    def put(self, id):
        args = rating_parser.parse_args()
        rating = Rating.query.get_or_404(id)

        if "campaign_id" in args:
            rating.campaign_id = args["campaign_id"]
        if "rating" in args:
            rating.rating = args["rating"]
        if "review" in args:
            rating.review = args["review"]
        if "ratee_id" in args:
            rating.ratee_id = args["ratee_id"]
        if "rater_id" in args:
            rating.rater_id = args["rater_id"]
        if "date" in args:
            rating.date = args["date"]
        db.session.commit()
        return rating, 200

    def delete(self, id):
        rating = Rating.query.get_or_404(id)
        db.session.delete(rating)
        db.session.commit()
        return "", 204
