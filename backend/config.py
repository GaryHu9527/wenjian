import os
from dataclasses import dataclass, field


def _bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    allowed_origins: tuple[str, ...] = field(default_factory=lambda: tuple(filter(None, os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(","))))
    ai_provider: str = field(default_factory=lambda: os.getenv("AI_PROVIDER", "openai_compatible"))
    ai_api_key: str = field(default_factory=lambda: os.getenv("AI_API_KEY", ""))
    ai_base_url: str = field(default_factory=lambda: os.getenv("AI_BASE_URL", ""))
    ai_model: str = field(default_factory=lambda: os.getenv("AI_MODEL", ""))
    zhihu_api_key: str = field(default_factory=lambda: os.getenv("ZHIHU_API_KEY", ""))
    zhihu_base_url: str = field(default_factory=lambda: os.getenv("ZHIHU_BASE_URL", "https://developer.zhihu.com"))
    use_mock_ai: bool = field(default_factory=lambda: _bool("USE_MOCK_AI", True))
    use_mock_zhihu: bool = field(default_factory=lambda: _bool("USE_MOCK_ZHIHU", True))
    jiayan_model_dir: str = field(default_factory=lambda: os.getenv("JIAYAN_MODEL_DIR", ""))
    cache_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL_SECONDS", "1800")))
