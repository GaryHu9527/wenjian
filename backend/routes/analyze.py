from flask import Blueprint, current_app, jsonify, request
from services.ai_service import AiServiceError

analyze_bp = Blueprint("analyze", __name__)
VALID_MODES = {"word", "grammar", "translation", "knowledge", "comprehensive"}

@analyze_bp.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True) or {}
    text, context, mode = payload.get("text"), payload.get("context", ""), payload.get("mode", "word")
    if not isinstance(text, str) or not text.strip(): return _error("INVALID_REQUEST", "text 不能为空", 400)
    if len(text) > 1000 or not isinstance(context, str) or len(context) > 3000: return _error("TEXT_TOO_LONG", "提交的文本过长", 400)
    if mode not in VALID_MODES: return _error("INVALID_MODE", "不支持的分析模式", 400)
    try:
        data = current_app.config["ANALYSIS_SERVICE"].analyze(text.strip(), context, payload.get("article"), mode)
        return jsonify(success=True, data=data)
    except AiServiceError as exc:
        return _error(exc.code, exc.message, exc.status)

def _error(code, message, status): return jsonify(success=False, error={"code": code, "message": message}), status
