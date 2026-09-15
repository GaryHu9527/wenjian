from flask import Blueprint, current_app, jsonify, request
from services.ai_service import AiServiceError
from services.request_ai import request_analysis_service

analyze_bp = Blueprint("analyze", __name__)
VALID_MODES = {"word", "grammar", "translation", "knowledge", "comprehensive"}

@analyze_bp.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "请求必须是 JSON 对象"}), 400
    if payload.get("article") is not None and not isinstance(payload["article"], dict):
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "article 参数格式错误"}), 400
    text, context, mode = payload.get("text"), payload.get("context", ""), payload.get("mode", "word")
    if not isinstance(text, str) or not text.strip(): return _error("INVALID_REQUEST", "text 不能为空", 400)
    if len(text) > 1000 or not isinstance(context, str) or len(context) > 3000: return _error("TEXT_TOO_LONG", "提交的文本过长", 400)
    if not isinstance(mode, str) or mode not in VALID_MODES: return _error("INVALID_MODE", "不支持的分析模式", 400)
    try:
        data = request_analysis_service().analyze(text.strip(), context, payload.get("article"), mode)
        return jsonify(success=True, data=data)
    except AiServiceError as exc:
        return _error(exc.code, exc.message, exc.status)

def _error(code, message, status): return jsonify(success=False, error={"code": code, "message": message}), status
