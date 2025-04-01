# app/__init__.py
import os
from flask import Flask, redirect
from flask_cors import CORS
from app.routes.api_routes import api_bp
from app.routes.llm_routes import llm_bp
from app.config import DevelopmentConfig, ProductionConfig


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def redirect_to_api():
        return redirect("/api/", code=302)

    # Instantiate the right config object
    if os.getenv("FLASK_ENV") == "production":
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()

    # Apply config object attributes to Flask config
    app.config.from_mapping(
        DEBUG=config.DEBUG,
        MONGO_URI=config.MONGO_URI,
        MONGO_INITDB_ROOT_USERNAME=config.MONGO_INITDB_ROOT_USERNAME,
        MONGO_INITDB_ROOT_PASSWORD=config.MONGO_INITDB_ROOT_PASSWORD,
        GOOGLE_API_KEY=config.GOOGLE_API_KEY,
        FRONTEND_ORIGINS=config.FRONTEND_ORIGINS,
    )

    # Set up CORS using the correct frontend origins
    CORS(
        app,
        origins=config.FRONTEND_ORIGINS,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"],
    )

    app.register_blueprint(api_bp)
    app.register_blueprint(llm_bp)

    return app
