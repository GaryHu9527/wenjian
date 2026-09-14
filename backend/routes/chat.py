from flask import Blueprint, current_app, jsonify, request
from services.ai_service import AiServiceError

chat_bp = Blueprint("chat", __name__)

@chat_bp.post("/api/chat")
def chat():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "请求必须是 JSON 对象"}), 400
    if payload.get("article") is not None and not isinstance(payload["article"], dict):
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "article 参数格式错误"}), 400
    question, text = payload.get("question"), payload.get("selected_text")
    if not isinstance(question, str) or not question.strip() or not isinstance(text, str) or not text.strip():
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "question 和 selected_text 不能为空"}), 400
    if len(question) > 1000 or len(text) > 1000:
        return jsonify(success=False, error={"code": "TEXT_TOO_LONG", "message": "提交的文本过长"}), 400
    try:
        data = current_app.config["AI_SERVICE"].answer_chat(question.strip(), text.strip(), payload.get("context"), payload.get("article"), payload.get("analysis"))
        return jsonify(success=True, data=data)
    except AiServiceError as exc:
        return jsonify(success=False, error={"code": exc.code, "message": exc.message}), exc.status
