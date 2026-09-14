from flask import Blueprint, current_app, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.get("/api/health")
def health():
    config = current_app.config["WENJIAN_CONFIG"]
    nlp = current_app.config["NLP_SERVICE"].analyze_classical_text("学而时习之")
    return jsonify(success=True, data={"backend": "ok", "ai_available": bool(config.ai_api_key and config.ai_base_url and config.ai_model) and not config.use_mock_ai, "zhihu_available": bool(config.zhihu_api_key) and not config.use_mock_zhihu, "ai_mode": "mock" if config.use_mock_ai else "remote", "classical_nlp_provider": nlp["provider"], "version": "0.2.0"})
