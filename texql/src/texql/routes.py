#! /usr/bin/env python3
import structlog
from flask import Blueprint, jsonify, request
from .agent import run_agent
from .config import bootstrap

logger = structlog.get_logger(__name__)

api = Blueprint("api", __name__)

services, config = bootstrap()


@api.post("/chat")
def create_message():
    data = request.get_json()

    userMsg = data.get("text")
    conversation_id = data["conversation_id"]

    if not userMsg:
        return jsonify({"error": "missing text"}), 400

    base_log = logger.bind(conversation_id=conversation_id)

    result = run_agent(userMsg, services, config, base_log)

    return jsonify(result)
