import hashlib
import logging
import requests
from prompts import SYSTEM_PROMPT, build_prompt
from utils.cache import MemoryCache
from utils.json_parser import JsonParseError, safe_parse_json

LOGGER = logging.getLogger(__name__)
VALID_MODES = {"word", "grammar", "translation", "knowledge", "comprehensive"}


class AiServiceError(Exception):
    def __init__(self, code, message, status=502):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


class AiService:
    def __init__(self, config):
        self.config = config
        self.cache = MemoryCache(config.cache_ttl_seconds)

    def analyze_text(self, text, context=None, article=None, mode="word", nlp_context=None, translation_reference=None):
        if mode not in VALID_MODES:
            raise AiServiceError("INVALID_MODE", "不支持的分析模式", 400)
        key = hashlib.sha256(f"{article}|{text}|{context}|{mode}|{nlp_context}|{translation_reference}".encode()).hexdigest()
        cached = self.cache.get(key)
        if cached:
            return cached
        result = self._mock_result(text, context, article, mode) if self.config.use_mock_ai else self._remote_result(text, context, article, mode, nlp_context, translation_reference)
        return self.cache.set(key, result)

    def _remote_result(self, text, context, article, mode, nlp_context=None, translation_reference=None):
        if not all([self.config.ai_api_key, self.config.ai_base_url, self.config.ai_model]):
            raise AiServiceError("AI_NOT_CONFIGURED", "分析服务尚未配置", 502)
        modes = ["word", "grammar", "translation", "knowledge"] if mode == "comprehensive" else [mode]
        output = {}
        for item_mode in modes:
            try:
                response = requests.post(f"{self.config.ai_base_url.rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {self.config.ai_api_key}", "Content-Type": "application/json"}, json={"model": self.config.ai_model, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_prompt(text, context, article, item_mode, nlp_context, translation_reference)}], "temperature": 0.2, "response_format": {"type": "json_object"}}, timeout=20)
            except requests.Timeout as exc:
                raise AiServiceError("AI_TIMEOUT", "分析服务响应较慢，请稍后重试", 502) from exc
            if response.status_code == 429:
                raise AiServiceError("AI_RATE_LIMITED", "分析服务繁忙，请稍后重试", 429)
            if not response.ok:
                raise AiServiceError("AI_REQUEST_FAILED", "分析服务暂时不可用", 502)
            try:
                content = response.json()["choices"][0]["message"]["content"]
                output[item_mode] = safe_parse_json(content)
            except (KeyError, ValueError, JsonParseError) as exc:
                raise AiServiceError("AI_INVALID_RESPONSE", "分析结果格式异常，请稍后重试", 502) from exc
        return output if mode == "comprehensive" else output[mode]

    def _mock_result(self, text, context, article, mode):
        article_name = (article or {}).get("title", "这篇文章")
        if mode == "comprehensive":
            return {name: self._mock_result(text, context, article, name) for name in ("word", "grammar", "translation", "knowledge")}
        if mode == "grammar":
            inverted = "谁" in text and ("与" in text or "何" in text)
            return {"summary": "宾语前置句" if inverted else "普通句式", "sentence_pattern": "宾语前置" if inverted else "普通句式", "modern_order": "请结合上下文调整语序" if inverted else text, "components": [{"text": text, "role": "核心句子"}], "explanation": "疑问代词作宾语时，古汉语常将宾语提前。" if inverted else "该句未见可确定的特殊句式。", "knowledge_point": "疑问代词作宾语的前置现象" if inverted else "结合上下文理解句意", "similar_pattern": "何以战？" if inverted else "", "confidence": "medium"}
        if mode == "translation":
            return {"literal": f"对“{text}”应逐字结合上下文理解。", "natural": f"这句话需放回《{article_name}》的语境中理解其完整含义。", "key_points": [{"text": text, "explanation": "当前为 Demo 规则化分析；配置 AI 后将生成完整译文。"}], "ambiguities": []}
        if mode == "knowledge":
            keywords = [name for name in ((article or {}).get("author"), article_name, "古代汉语", "历史语境") if name]
            return {"summary": f"“{text}”可从作品语境、人物经历与时代思想三个层面继续探索。", "people": ([{"name": (article or {}).get("author"), "description": f"《{article_name}》的作者。"}] if (article or {}).get("author") else []), "events": [], "allusions": [], "historical_context": "建议结合文章写作年代与作者政治、文化处境阅读。", "literary_context": f"《{article_name}》的篇章结构与表达方式会影响这句话的含义。", "thought_context": "可进一步考察儒家公共伦理与士人理想。", "keywords": keywords[:5], "questions": [f"{article_name}的写作背景是什么？", f"“{text}”体现了怎样的思想？"]}
        return {"summary": f"“{text}”需要结合上下文释义。", "items": [{"text": text, "meaning": "请结合语境理解其在句中的具体含义。", "original_meaning": "待 AI 服务配置后细化", "type": "普通释义", "part_of_speech": "待定", "usage": context or "未提供上下文", "note": "当前为 Demo 规则化分析，不强行判断通假或活用。", "confidence": "low"}]}

    def answer_chat(self, question, selected_text, context=None, article=None, analysis=None):
        if self.config.use_mock_ai:
            return {"answer": f"围绕“{selected_text}”，可以先从句法位置、上下文与篇章主旨三方面理解：{question}。当前 Demo 使用本地规则回答；配置 AI 服务后会给出更具体的教学解释。", "related_questions": ["这句话在全文中起什么作用？", "是否有相似句式？"]}
        result = self._remote_result(selected_text, context, article, "knowledge")
        return {"answer": result.get("summary", "暂无法生成回答"), "related_questions": result.get("questions", [])}
