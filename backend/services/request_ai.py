"""Request-scoped credentials; never mutate the shared application configuration."""
import re
from dataclasses import replace
from flask import request, current_app
from services.ai_service import AiService, AiServiceError
from services.analysis_service import AnalysisService


def request_ai_service():
    key = request.headers.get('X-AI-Key')
    if key is None:
        return current_app.config['AI_SERVICE']
    bases = {'deepseek': 'https://api.deepseek.com', 'openai': 'https://api.openai.com/v1'}
    provider, model = request.headers.get('X-AI-Provider'), request.headers.get('X-AI-Model', '')
    if provider not in bases or not re.fullmatch(r'[\x21-\x7e]{1,512}', key) or not re.fullmatch(r'[a-zA-Z0-9._:/-]{1,128}', model):
        raise AiServiceError('AI_CONFIG_INVALID', '请检查服务商、模型名称和 API Key。', 400)
    config = replace(current_app.config['WENJIAN_CONFIG'], ai_api_key=key, ai_base_url=bases[provider], ai_model=model, use_mock_ai=False)
    return AiService(config)


def request_analysis_service():
    if request.headers.get('X-AI-Key') is None:
        return current_app.config['ANALYSIS_SERVICE']
    return AnalysisService(request_ai_service(), current_app.config['NLP_SERVICE'], current_app.config['CORPUS_PROVIDER'])
