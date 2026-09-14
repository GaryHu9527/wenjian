SYSTEM_PROMPT = """你是一名严谨的古代汉语教学助手。结合上下文分析，不虚构出处、通假或词类活用；不确定时明确标记不确定。翻译需区分直译和意译。只输出严格 JSON，不输出 Markdown 或其他文字。"""

MODE_SCHEMAS = {
    "word": '{"summary":"","items":[{"text":"","meaning":"","original_meaning":"","type":"普通释义","part_of_speech":"","usage":"","note":"","confidence":"high"}]}',
    "grammar": '{"summary":"","sentence_pattern":"普通句式","modern_order":"","components":[{"text":"","role":""}],"explanation":"","knowledge_point":"","similar_pattern":"","confidence":"high"}',
    "translation": '{"literal":"","natural":"","key_points":[{"text":"","explanation":""}],"ambiguities":[]}',
    "knowledge": '{"summary":"","people":[{"name":"","description":""}],"events":[],"allusions":[],"historical_context":"","literary_context":"","thought_context":"","keywords":[""],"questions":[""]}',
}

def build_prompt(text, context, article, mode, nlp_context=None, translation_reference=None):
    nlp_note = "未提供" if not nlp_context else str(nlp_context)
    reference_note = "未提供" if not translation_reference or not translation_reference.get("matched") else str(translation_reference)
    return f"模式：{mode}\n文章：{(article or {}).get('title', '')}\n上下文：{context or '未提供'}\n待分析文本：{text}\nNLP 辅助信息（可能有误，只作参考；请独立判断）：{nlp_note}\n参考译文（不一定适用于当前上下文，请独立判断）：{reference_note}\n输出结构：{MODE_SCHEMAS[mode]}"
