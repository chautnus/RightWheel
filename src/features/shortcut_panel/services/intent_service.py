"""Intent-Based Action & Shortcut Catalog and Search Service.

Allows users to search actions by their goal/purpose in Vietnamese or English
(e.g., 'task manager', 'chụp màn hình', 'đổi tab') and auto-fills the key combo.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any


def _normalize_str(text: str) -> str:
    """Normalize text: lowercase, strip accents/diacritics for flexible fuzzy matching."""
    text = text.lower().strip()
    text = text.replace("đ", "d").replace("Đ", "d")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


@dataclass
class IntentItem:
    intent_id: str
    title_vi: str
    title_en: str
    keys: str
    category: str
    keywords: list[str]
    description: str = ""

    def match_score(self, query: str) -> int:
        """Calculate match relevance score (higher is better). 0 means no match."""
        if not query:
            return 1
        q_norm = _normalize_str(query)
        score = 0

        # Exact title match
        if q_norm == _normalize_str(self.title_vi) or q_norm == _normalize_str(self.title_en):
            return 100

        # Direct containment in title
        if q_norm in _normalize_str(self.title_vi) or q_norm in _normalize_str(self.title_en):
            score += 40

        # Direct containment in keys
        if q_norm in _normalize_str(self.keys):
            score += 50

        # Match in keywords
        for kw in self.keywords:
            kw_norm = _normalize_str(kw)
            if q_norm == kw_norm:
                score += 35
            elif q_norm in kw_norm:
                score += 20
            elif all(word in kw_norm for word in q_norm.split()):
                score += 15

        return score


class IntentService:
    """Service providing fuzzy and intent-based lookup for keyboard shortcuts."""

    def __init__(self, catalog: list[IntentItem] | None = None) -> None:
        if catalog is not None:
            self.catalog = catalog
        else:
            from .intent_catalog_data import INTENT_CATALOG
            self.catalog = INTENT_CATALOG

    def search(self, query: str, limit: int = 15) -> list[IntentItem]:
        """Search intents matching query, sorted by relevance score."""
        q = query.strip()
        if not q:
            return self.catalog[:limit]

        scored: list[tuple[int, IntentItem]] = []
        for item in self.catalog:
            score = item.match_score(q)
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def get_by_id(self, intent_id: str) -> IntentItem | None:
        for it in self.catalog:
            if it.intent_id == intent_id:
                return it
        return None

    def get_all_categories(self) -> list[str]:
        cats: list[str] = []
        for it in self.catalog:
            if it.category not in cats:
                cats.append(it.category)
        return cats

    def get_by_category(self, category: str) -> list[IntentItem]:
        return [it for it in self.catalog if it.category == category]
