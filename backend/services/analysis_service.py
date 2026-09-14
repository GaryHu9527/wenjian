"""Orchestrates optional local enhancement services without coupling them together."""
from services.classical_corpus import ClassicalCorpusProvider
from services.translation_reference import TranslationReferenceService


class AnalysisService:
    def __init__(self, ai_service, nlp_service, corpus_provider=None, translation_references=None):
        self.ai_service = ai_service
        self.nlp_service = nlp_service
        self.corpus_provider = corpus_provider or ClassicalCorpusProvider(ai_service.config.cache_ttl_seconds)
        self.translation_references = translation_references or TranslationReferenceService()

    def analyze(self, text, context=None, article=None, mode="word"):
        nlp = self.nlp_service.analyze_classical_text(text) if mode in {"word", "grammar", "comprehensive"} else None
        reference = self.translation_references.find_translation_reference(text) if mode in {"translation", "comprehensive"} else None
        corpus_items = self.corpus_provider.search(text, [((article or {}).get("title", ""))]) if mode in {"knowledge", "comprehensive"} else []
        analysis = self.ai_service.analyze_text(text, context, article, mode, nlp_context=nlp, translation_reference=reference)
        # Keep legacy top-level analysis fields for the existing Vue panels, while exposing structured enhancements.
        if mode == "comprehensive":
            return {"nlp": nlp, "translation_reference": reference, "corpus": corpus_items, "analysis": analysis, **analysis}
        return {"nlp": nlp, "translation_reference": reference, "corpus": corpus_items, "analysis": analysis, **analysis}
