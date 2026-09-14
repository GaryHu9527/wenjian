import json
import re

class JsonParseError(ValueError):
    pass

def safe_parse_json(raw):
    if not isinstance(raw, str):
        raise JsonParseError("模型响应不是文本")
    cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw.strip(), flags=re.I)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start:end + 1]
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise JsonParseError("模型返回的结构化数据无法解析") from exc
    if not isinstance(value, dict):
        raise JsonParseError("模型返回的数据格式不正确")
    return value
