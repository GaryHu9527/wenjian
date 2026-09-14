import unittest
from app import create_app
from config import Config


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app(Config(use_mock_ai=True, use_mock_zhihu=True)).test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

    def test_grammar(self):
        response = self.client.post("/api/analyze", json={"text": "吾谁与归", "context": "微斯人，吾谁与归？", "mode": "grammar"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["sentence_pattern"], "宾语前置")

    def test_invalid_mode(self):
        response = self.client.post("/api/analyze", json={"text": "测试", "mode": "invalid"})
        self.assertEqual(response.status_code, 400)

    def test_other_analysis_modes(self):
        for mode in ("word", "translation", "knowledge", "comprehensive"):
            response = self.client.post("/api/analyze", json={"text": "先天下之忧而忧", "article": {"title": "岳阳楼记", "author": "范仲淹"}, "mode": mode})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.get_json()["success"])

    def test_analyze_includes_optional_enhancements(self):
        response = self.client.post("/api/analyze", json={"text": "学而时习之", "mode": "translation", "article": {"title": "论语", "author": "孔子"}})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertTrue(data["translation_reference"]["matched"])
        self.assertIn("analysis", data)

    def test_corpus_search(self):
        response = self.client.post("/api/corpus/search", json={"query": "学而时习之", "keywords": ["论语"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["data"]["items"][0]["title"], "论语·学而篇")

    def test_zhihu_mock(self):
        response = self.client.post("/api/zhihu/search", json={"text": "先天下之忧而忧", "article": {"title": "岳阳楼记", "author": "范仲淹"}})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["data"]["related_questions"])
        self.assertEqual(response.get_json()["data"]["source_mode"], "mock")

    def test_chat(self):
        response = self.client.post("/api/chat", json={"question": "为什么这里是宾语前置？", "selected_text": "吾谁与归", "context": "微斯人，吾谁与归？"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("answer", response.get_json()["data"])

if __name__ == "__main__":
    unittest.main()

class ConfigurationRegressionTests(unittest.TestCase):
    def test_environment_is_read_when_config_is_created(self):
        import os
        from unittest.mock import patch
        with patch.dict(os.environ, {"USE_MOCK_AI": "false", "AI_MODEL": "regression-model"}):
            config = Config()
            self.assertFalse(config.use_mock_ai)
            self.assertEqual(config.ai_model, "regression-model")

    def test_remote_chat_sends_the_actual_question(self):
        from unittest.mock import Mock, patch
        from services.ai_service import AiService
        config = Config(use_mock_ai=False, ai_api_key="test", ai_base_url="https://example.test/v1", ai_model="test")
        response = Mock(status_code=200, ok=True)
        response.json.return_value = {"choices": [{"message": {"content": '{"answer":"谁是宾语","related_questions":[]}'}}]}
        with patch("services.ai_service.requests.post", return_value=response) as post:
            answer = AiService(config).answer_chat("谁作什么成分？", "吾谁与归")
            self.assertIn("谁作什么成分", post.call_args.kwargs["json"]["messages"][-1]["content"])
            self.assertEqual(answer["answer"], "谁是宾语")

class ProjectBriefTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app(Config(use_mock_ai=True, use_mock_zhihu=True)).test_client()

    def test_corpus_alias(self):
        response = self.client.post('/api/corpus', json={'query': '温故而知新'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['data']['items'])

    def test_query_contains_all_context_and_demo_categories(self):
        from services.zhihu_service import ZhihuService
        service = ZhihuService(Config(use_mock_zhihu=True))
        result = service.demo_result('先天下之忧而忧', {'title': '岳阳楼记', 'author': '范仲淹', 'dynasty': '北宋'})
        for term in ['范仲淹', '岳阳楼记', '北宋', '先天下之忧而忧']:
            self.assertIn(term, result['query'])
        self.assertEqual({i['category'] for i in result['items']}, {'discussion','question','column','person'})

    def test_bad_payload_is_a_client_error(self):
        for route in ['/api/analyze','/api/chat','/api/corpus','/api/zhihu/search']:
            self.assertEqual(self.client.post(route, json=[1]).status_code, 400)
        self.assertEqual(self.client.post('/api/zhihu/search', json={'text':'测试', 'count':'bad'}).status_code, 400)

    def test_rule_fallback_without_jiayan(self):
        from services.classical_nlp import ClassicalNlpService
        result = ClassicalNlpService().analyze_classical_text('学而时习之。不亦说乎？')
        self.assertEqual(result['provider'], 'rules')
        self.assertEqual(len(result['sentences']), 2)
