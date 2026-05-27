from functools import lru_cache
import os
import re

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_reranker(model_name: str):
    from huggingface_hub import snapshot_download
    from sentence_transformers import CrossEncoder

    settings = get_settings()
    cache_dir = str(settings.path(settings.hf_cache_dir))
    os.environ.setdefault("HF_HOME", cache_dir)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", cache_dir)
    logger.info("Loading reranker model: %s", model_name)
    try:
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=True,
        )
    except Exception:
        logger.info("Reranker model not found in cache; downloading: %s", model_name)
        model_path = snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False,
        )
    return CrossEncoder(
        model_path,
        local_files_only=True,
        model_kwargs={},
        processor_kwargs={},
        config_kwargs={},
    )


def warmup_reranker() -> None:
    settings = get_settings()
    _load_reranker(settings.reranker_model)


class RerankService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def rerank(self, question: str, chunks: list[dict]) -> list[dict]:
        if not chunks:
            return []
        try:
            model = _load_reranker(self.settings.reranker_model)
            pairs = [(question, chunk["text"]) for chunk in chunks]
            scores = model.predict(pairs)
            ranked = []
            for chunk, score in zip(chunks, scores, strict=False):
                lexical_boost = self._relevance_boost(question, chunk)
                intro_penalty = self._generic_intro_penalty(question, chunk)
                adjusted_score = float(score) + lexical_boost - intro_penalty
                ranked.append(
                    {
                        **chunk,
                        "rerank_score": float(score),
                        "lexical_boost": lexical_boost,
                        "intro_penalty": intro_penalty,
                        "score": adjusted_score,
                    }
                )
            ranked = sorted(ranked, key=lambda item: item["score"], reverse=True)
            self._log_ranked("CrossEncoder reranked", ranked)
            return ranked
        except Exception as exc:
            logger.warning("Reranker unavailable, using vector scores only: %s", exc)
            boosted = []
            for chunk in chunks:
                lexical_boost = self._relevance_boost(question, chunk)
                intro_penalty = self._generic_intro_penalty(question, chunk)
                boosted.append(
                    {
                        **chunk,
                        "lexical_boost": lexical_boost,
                        "intro_penalty": intro_penalty,
                        "score": float(chunk.get("score") or 0) + lexical_boost - intro_penalty,
                    }
                )
            ranked = sorted(boosted, key=lambda item: item["score"], reverse=True)
            self._log_ranked("Vector fallback reranked", ranked)
            return ranked

    def _query_terms(self, question: str) -> set[str]:
        stop_words = {
            "a",
            "an",
            "and",
            "about",
            "tell",
            "me",
            "the",
            "to",
            "of",
            "for",
            "in",
            "on",
            "what",
            "is",
            "are",
        }
        return {
            token
            for token in re.findall(r"[a-z0-9]+", question.lower())
            if len(token) > 2 and token not in stop_words
        }

    def _relevance_boost(self, question: str, chunk: dict) -> float:
        text = (chunk.get("text") or "").lower()
        normalized_question = " ".join(re.findall(r"[a-z0-9]+", question.lower()))
        terms = self._query_terms(question)
        boost = 0.0

        if normalized_question and normalized_question in " ".join(re.findall(r"[a-z0-9]+", text)):
            boost += 2.0

        matched_terms = [term for term in terms if term in text]
        if terms:
            boost += min(1.5, len(matched_terms) / len(terms) * 1.5)

        phrase_boosts = (
            ("building a data model", 3.0),
            ("building data model", 2.5),
            ("introduction to data modeling", 3.0),
            ("data modeling", 2.0),
            ("data model", 1.75),
            ("e-commerce data model", 3.0),
            ("ecommerce data model", 3.0),
            ("database model", 1.5),
            ("schema", 1.0),
            ("entity", 0.75),
            ("entities", 0.75),
            ("relationship", 0.75),
            ("relationships", 0.75),
        )
        question_mentions_data_model = any(
            phrase in normalized_question
            for phrase in ("data model", "data modeling", "e commerce", "ecommerce")
        )
        if question_mentions_data_model:
            for phrase, value in phrase_boosts:
                if phrase in text:
                    boost += value

        if chunk.get("timestamp_label") or chunk.get("timestamp") is not None:
            boost += 0.15

        if self._looks_like_chapter_title(text, terms):
            boost += 1.0

        return boost

    def _looks_like_chapter_title(self, text: str, terms: set[str]) -> bool:
        first_words = " ".join(text.split()[:18])
        title_markers = ("chapter", "section", "lesson", "introduction", "building", "model")
        if any(marker in first_words for marker in title_markers) and any(term in first_words for term in terms):
            return True
        return False

    def _log_ranked(self, label: str, chunks: list[dict]) -> None:
        for index, chunk in enumerate(chunks[:10], start=1):
            text = " ".join((chunk.get("text") or "").split())[:220]
            logger.info(
                "%s %s score=%s rerank_score=%s vector_score=%s lexical_boost=%s "
                "intro_penalty=%s timestamp=%s text=%s",
                label,
                index,
                chunk.get("score"),
                chunk.get("rerank_score"),
                chunk.get("vector_score"),
                chunk.get("lexical_boost"),
                chunk.get("intro_penalty"),
                chunk.get("timestamp_label") or chunk.get("timestamp"),
                text,
            )

    def _generic_intro_penalty(self, question: str, chunk: dict) -> float:
        question_terms = question.lower()
        if any(term in question_terms for term in ("intro", "introduction", "overview")):
            return 0
        text = (chunk.get("text") or "").lower()
        timestamp = float(chunk.get("timestamp") or chunk.get("start") or 0)
        generic_markers = (
            "welcome to",
            "in this course",
            "subscribe",
            "jump in and get started",
            "ultimate",
            "course for you",
        )
        if timestamp <= 90 and any(marker in text for marker in generic_markers):
            return 2.0
        return 0
