from __future__ import annotations

import json
from difflib import SequenceMatcher
from pathlib import Path


class TranslationReferenceService:
    def __init__(self):
        seed = Path(__file__).resolve().parent.parent / "data" / "cctc_seed.json"
        self.items = json.loads(seed.read_text(encoding="utf-8"))

    def find_translation_reference(self, text):
        normalized = "".join((text or "").split())
        if not normalized: return {"matched": False, "source": "", "target": "", "similarity": 0.0}
        def score(item):
            candidate = "".join(item["source"].split())
            return 0.95 if normalized in candidate else SequenceMatcher(None, normalized, candidate).ratio()
        best = max(self.items, key=score)
        similarity = score(best)
        return {"matched": similarity >= 0.55, "source": best["source"] if similarity >= 0.55 else "", "target": best["target"] if similarity >= 0.55 else "", "similarity": round(similarity, 3), "dataset": best["dataset"] if similarity >= 0.55 else ""}
