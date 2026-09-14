import logging
import os
import time
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from config import Config
from routes import ALL_BLUEPRINTS
from services.ai_service import AiService
from services.analysis_service import AnalysisService
from services.classical_corpus import ClassicalCorpusProvider
from services.classical_nlp import ClassicalNlpService
from services.translation_reference import TranslationReferenceService
from services.zhihu_service import ZhihuService

load_dotenv()

def create_app():
    app = Flask(__name__)
    config = Config()
    CORS(app, resources={r"/api/*": {"origins": list(config.allowed_origins)}})
    app.config["WENJIAN_CONFIG"] = config
    app.config["AI_SERVICE"] = AiService(config)
    app.config["CORPUS_PROVIDER"] = ClassicalCorpusProvider(config.cache_ttl_seconds)
    app.config["NLP_SERVICE"] = ClassicalNlpService(config.jiayan_model_dir)
    app.config["ANALYSIS_SERVICE"] = AnalysisService(app.config["AI_SERVICE"], app.config["NLP_SERVICE"], app.config["CORPUS_PROVIDER"], TranslationReferenceService())
    app.config["ZHIHU_SERVICE"] = ZhihuService(config)
    @app.before_request
    def start_timer():
        g.request_started_at = time.perf_counter()

    @app.after_request
    def log_request(response):
        if request.path.startswith("/api/"):
            elapsed_ms = (time.perf_counter() - g.get("request_started_at", time.perf_counter())) * 1000
            app.logger.info("api_request path=%s status=%s duration_ms=%.1f", request.path, response.status_code, elapsed_ms)
        return response

    for blueprint in ALL_BLUEPRINTS:
        app.register_blueprint(blueprint)

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(success=False, error={"code": "NOT_FOUND", "message": "接口不存在"}), 404

    @app.errorhandler(500)
    def server_error(_):
        app.logger.exception("Unhandled backend error")
        return jsonify(success=False, error={"code": "INTERNAL_ERROR", "message": "服务暂时不可用，请稍后重试"}), 500
    return app

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", os.getenv("FLASK_PORT", "5000"))), debug=os.getenv("FLASK_ENV") == "development")
