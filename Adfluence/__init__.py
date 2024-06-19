from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    api = Api(app)
    app.config["SECRET_KEY"] = "idkra&w"
    app.config["UPLOAD_FOLDER"] = "Adfluence/static/uploads"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .sponsor import sponsor
    from .admin import admin
    from .influencer import influencer

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(sponsor, url_prefix="/sponsor")
    app.register_blueprint(influencer, url_prefix="/influencer")

    from .models import User

    with app.app_context():
        db.create_all()
    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .api import CampaignAPI
    from .api import AdRequestAPI
    from .api import UserAPI
    from .api import InfluencerAPI
    from .api import CampaignRequestAPI

    api.add_resource(UserAPI, "/api/user/<int:id>", "/api/user")
    api.add_resource(CampaignAPI, "/api/campaign/<int:id>", "/api/campaign")
    api.add_resource(AdRequestAPI, "/api/adrequest/<int:id>", "/api/adrequest")
    api.add_resource(CampaignRequestAPI, "/api/CampaignRequest/<int:id>", "/api/CampaignRequest")
    api.add_resource(InfluencerAPI, "/api/influencer/<int:id>", "/api/influencer")
    return app

