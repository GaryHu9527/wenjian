"""Optional Jiayan adapter.  Model files are deliberately not bundled with the app."""
from __future__ import annotations

import os
import re
from pathlib import Path


class ClassicalNlpService:
    def __init__(self, model_dir=None):
        self.model_dir = Path(model_dir or os.getenv("JIAYAN_MODEL_DIR", "")) if (model_dir or os.getenv("JIAYAN_MODEL_DIR")) else None
        self._tools = None

    def _load(self):
        if self._tools is not None:
            return self._tools
        if not self.model_dir or not all((self.model_dir / name).exists() for name in ("jiayan.klm", "pos_model", "cut_model", "punc_model")):
            self._tools = False
            return False
        try:
            from jiayan import CharHMMTokenizer, CRFPOSTagger, CRFSentencizer, CRFPunctuator, load_lm
            lm = load_lm(str(self.model_dir / "jiayan.klm"))
            pos = CRFPOSTagger(); pos.load(str(self.model_dir / "pos_model"))
            sentencizer = CRFSentencizer(lm); sentencizer.load(str(self.model_dir / "cut_model"))
            punctuator = CRFPunctuator(lm, str(self.model_dir / "cut_model")); punctuator.load(str(self.model_dir / "punc_model"))
            self._tools = (CharHMMTokenizer(lm), pos, sentencizer, punctuator)
        except Exception:
            self._tools = False
        return self._tools

    def analyze_classical_text(self, text):
        result = {"text": text, "tokens": [], "pos": [], "sentences": [], "punctuated_text": None, "provider": "unavailable"}
        tools = self._load()
        if not tools:
            result.update({"provider": "rules", "sentences": [part.strip() for part in re.split(r"[。！？!?]", text) if part.strip()], "warning": "未加载 Jiayan 模型；仅按标点分句，不提供模型词性标注。"})
            return result
        try:
            tokenizer, tagger, sentencizer, punctuator = tools
            tokens = list(tokenizer.tokenize(text))
            result.update({
                "tokens": tokens,
                "pos": [{"token": token, "tag": tag} for token, tag in zip(tokens, tagger.postag(tokens))],
                "sentences": list(sentencizer.sentencize(text)) if re.search(r"[^。！？!?]", text) else [part for part in re.split(r"[。！？!?]", text) if part],
                "punctuated_text": punctuator.punctuate(text),
                "provider": "jiayan",
            })
        except Exception as exc:
            result["warning"] = f"Jiayan 处理失败：{type(exc).__name__}"
        return result
