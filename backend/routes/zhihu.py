from flask import Blueprint, current_app, jsonify, request
from services.zhihu_service import ZhihuServiceError

zhihu_bp = Blueprint("zhihu", __name__)

@zhihu_bp.post("/api/zhihu/search")
def search():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "请求必须是 JSON 对象"}), 400
    if payload.get("article") is not None and not isinstance(payload["article"], dict):
        return jsonify(success=False, error={"code": "INVALID_REQUEST", "message": "article 参数格式错误"}), 400
    text = payload.get("text", "")
    if not isinstance(text, str) or not text.strip(): return _error("INVALID_REQUEST", "text 不能为空", 400)
    if len(text) > 1000: return _error("TEXT_TOO_LONG", "搜索文本过长", 400)
    count = payload.get("count", 5)
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 5:
        return _error("INVALID_REQUEST", "count 须为 1 至 5 的整数", 400)
    if payload.get("keywords") is not None and (not isinstance(payload["keywords"], list) or any(not isinstance(k, str) for k in payload["keywords"])):
        return _error("INVALID_REQUEST", "keywords 须为字符串数组", 400)
    if payload.get("engine") == "mock":
        data = current_app.config["ZHIHU_SERVICE"].demo_result(text.strip(), payload.get("article"), count)
        return jsonify(success=True, data=data)
    try:
        data = current_app.config["ZHIHU_SERVICE"].search_zhihu(text.strip(), payload.get("article"), payload.get("keywords"), count)
        return jsonify(success=True, data=data)
    except ZhihuServiceError as exc:
        return _error(exc.code, exc.message, exc.status)

def _error(code, message, status): return jsonify(success=False, error={"code": code, "message": message}), status
