from flask import Blueprint, jsonify, request
from app.services.llm import gemini_summarize as summarize_impl

llm_bp = Blueprint("llm", __name__, url_prefix="/api")


@llm_bp.route("/summarize", methods=["POST"])
def gemini_summarize():
    return summarize_impl(request)
