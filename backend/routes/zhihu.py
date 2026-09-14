from flask import Blueprint, current_app, jsonify, request
from services.zhihu_service import ZhihuServiceError

zhihu_bp = Blueprint("zhihu", __name__)

@zhihu_bp.post("/api/zhihu/search")
def search():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    if not isinstance(text, str) or not text.strip(): return _error("INVALID_REQUEST", "text 不能为空", 400)
    if len(text) > 1000: return _error("TEXT_TOO_LONG", "搜索文本过长", 400)
    try:
        data = current_app.config["ZHIHU_SERVICE"].search_zhihu(text.strip(), payload.get("article"), payload.get("keywords"), min(int(payload.get("count", 5)), 5))
        return jsonify(success=True, data=data)
    except ZhihuServiceError as exc:
        return _error(exc.code, exc.message, exc.status)

def _error(code, message, status): return jsonify(success=False, error={"code": code, "message": message}), status
