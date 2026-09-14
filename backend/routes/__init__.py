from .analyze import analyze_bp
from .chat import chat_bp
from .corpus import corpus_bp
from .health import health_bp
from .zhihu import zhihu_bp

ALL_BLUEPRINTS = (health_bp, analyze_bp, zhihu_bp, chat_bp, corpus_bp)
