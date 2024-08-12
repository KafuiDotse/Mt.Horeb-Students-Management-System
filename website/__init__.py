from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db=SQLAlchemy()

def create_app():
    app=Flask(__name__)
    app.config["SECRET_KEY"]="29604849d9c60dfa378e13c75c65146d"
    app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://database_cyab_user:RA3qXzBUYUsP4XJxSG8O2KxszBuT4MGx@dpg-cm74asa1hbls73arp8rg-a.oregon-postgres.render.com/database_cyab"
    db.init_app(app)

    from .dbModels import User,Course

    with app.app_context():
        db.create_all()

    from .views import views
    from .auth import auth

    app.register_blueprint(views,url_prefix="/")
    app.register_blueprint(auth,url_prefix="/")

    login_manager=LoginManager()
    login_manager.login_view="auth.hero"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_db():
    if not path.exists("website/datebase.db"):
        db.create_all()
        print("Db created")