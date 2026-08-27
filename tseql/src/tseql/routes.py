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

    user_msg = data.get("text")
    conversation_id = data["conversation_id"]

    base_log = logger.bind(conversation_id=conversation_id)

    base_log.info(
        "chat_request_received",
        has_text=bool(user_msg),
        user_message=user_msg,
    )

    if not conversation_id:
        base_log.warning("missing_conversation_id")
        return jsonify({"error": "missing conversation_id"}), 400

    if not user_msg:
        base_log.warning("missing_text")
        return jsonify({"error": "missing text"}), 400

    result = run_agent(
        user_msg=user_msg,
        services=services,
        config=config,
        base_log=base_log,
    )

    table = result.get("table") if isinstance(result, dict) else None

    base_log.info(
        "chat_request_completed",
        has_table=bool(table),
        row_count=table.get("row_count", 0) if table else 0,
    )

    return jsonify(result)
