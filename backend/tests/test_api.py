import unittest
from app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

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
