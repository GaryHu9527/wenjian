from flask import Blueprint, current_app, jsonify, request

corpus_bp = Blueprint("corpus", __name__)

@corpus_bp.post("/api/corpus/search")
def search():
    payload = request.get_json(silent=True) or {}
    query, keywords = payload.get("query", ""), payload.get("keywords", [])
    if not isinstance(query, str) or not query.strip(): return _error("INVALID_REQUEST", "query 不能为空", 400)
    if len(query) > 200 or not isinstance(keywords, list): return _error("INVALID_REQUEST", "检索参数不合法", 400)
    safe_keywords = [word.strip() for word in keywords[:8] if isinstance(word, str) and word.strip()][:8]
    items = current_app.config["CORPUS_PROVIDER"].search(query.strip(), safe_keywords)
    return jsonify(success=True, data={"items": items})

def _error(code, message, status): return jsonify(success=False, error={"code": code, "message": message}), status
