import hashlib
import time
import requests
from mock.zhihu import MOCK_ZHIHU_RESULTS
from utils.cache import MemoryCache


class ZhihuServiceError(Exception):
    def __init__(self, code, message, status=502):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


class ZhihuService:
    def __init__(self, config):
        self.config = config
        self.cache = MemoryCache(config.cache_ttl_seconds)

    def generate_query(self, text, article=None, keywords=None):
        article = article or {}
        parts = [article.get("author", ""), article.get("title", ""), *(keywords or []), text]
        return " ".join(part.strip() for part in parts if isinstance(part, str) and part.strip())[:50]

    def search_zhihu(self, text, article=None, keywords=None, count=5):
        query = self.generate_query(text, article, keywords)
        key = hashlib.sha256(f"{query}|{count}".encode()).hexdigest()
        cached = self.cache.get(key)
        if cached:
            return cached
        if self.config.use_mock_zhihu:
            items = MOCK_ZHIHU_RESULTS[:count]
            result = {"query": query, "items": items, "related_questions": self._related_questions(items, article, text), "source_mode": "mock"}
        else:
            items = self._search_remote(query, count)
            # 关联问题从同一次真实检索中提炼，避免为侧栏额外消耗一次知乎 API 配额。
            result = {"query": query, "items": items, "related_questions": self._related_questions(items, article, text), "source_mode": "zhihu"}
        return self.cache.set(key, result)

    @staticmethod
    def _related_questions(items, article, text):
        questions, seen = [], set()
        markers = ("如何", "什么", "为何", "为什么", "怎样", "吗", "？", "?", "何以")
        for item in items:
            title = (item.get("title") or "").strip()
            if title and title not in seen and any(marker in title for marker in markers):
                questions.append({"title": title, "url": item.get("url")})
                seen.add(title)
            if len(questions) == 4:
                return questions
        article_title = (article or {}).get("title", "这篇文章")
        focus = (text or "文本")[:18]
        primary_question = f"如何理解《{article_title}》？" if focus == article_title else f"如何理解《{article_title}》中的“{focus}”？"
        for title in (primary_question, f"《{article_title}》的写作背景与思想主旨是什么？"):
            if title not in seen:
                questions.append({"title": title, "url": None})
        return questions[:4]

    def _search_remote(self, query, count):
        if not self.config.zhihu_api_key:
            raise ZhihuServiceError("ZHIHU_NOT_CONFIGURED", "知乎搜索服务尚未配置", 502)
        try:
            response = requests.get(f"{self.config.zhihu_base_url.rstrip('/')}/api/v1/content/zhihu_search", params={"Query": query, "Count": min(count, 5)}, headers={"Authorization": f"Bearer {self.config.zhihu_api_key}", "X-Request-Timestamp": str(int(time.time())), "Content-Type": "application/json"}, timeout=12)
        except requests.Timeout as exc:
            raise ZhihuServiceError("ZHIHU_TIMEOUT", "知乎搜索响应较慢，请稍后重试", 502) from exc
        except requests.RequestException as exc:
            raise ZhihuServiceError("ZHIHU_CONNECTION_ERROR", "知乎连接暂时不可用", 502) from exc
        if response.status_code == 429:
            raise ZhihuServiceError("ZHIHU_RATE_LIMITED", "知乎搜索服务繁忙，请稍后重试", 429)
        if not response.ok:
            raise ZhihuServiceError("ZHIHU_REQUEST_FAILED", "知乎搜索暂时不可用", 502)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ZhihuServiceError("ZHIHU_INVALID_RESPONSE", "知乎返回格式异常", 502) from exc
        if "rate limit" in str(payload.get("Message", "")).lower():
            raise ZhihuServiceError("ZHIHU_RATE_LIMITED", "知乎检索暂时限流，可使用站内搜索入口", 429)
        if payload.get("Code") not in (None, 0):
            raise ZhihuServiceError("ZHIHU_API_ERROR", payload.get("Message", "知乎搜索失败"), 502)
        return [self._normalize(item) for item in payload.get("Data", {}).get("Items", [])[:5]]

    @staticmethod
    def _normalize(item):
        return {"title": item.get("Title"), "excerpt": item.get("ContentText"), "url": item.get("Url"), "author": item.get("AuthorName"), "author_url": item.get("AuthorUrl") or item.get("AuthorURL"), "type": item.get("ContentType"), "image": item.get("AuthorAvatar"), "stats": {"vote_up_count": item.get("VoteUpCount"), "comment_count": item.get("CommentCount")}}
