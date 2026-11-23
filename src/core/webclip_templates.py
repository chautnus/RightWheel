"""Built-in searchable WebClip templates for popular web search and AI tools."""
from __future__ import annotations

from typing import Any
import unicodedata


def _fold_ascii(text: str) -> str:
    """Fold Unicode/Vietnamese diacritics to lowercase ASCII for accent-insensitive matching."""
    nfd = unicodedata.normalize("NFD", (text or "").lower())
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn").replace(chr(0x0111), "d")


BUILTIN_WEBCLIP_TEMPLATES: list[dict[str, Any]] = [
    {
        "id": "google_search",
        "name": "Google Search",
        "keywords": "google search tim kiem web tra cuu",
        "url_template": "https://www.google.com/search?q={text}",
        "base_url": "https://www.google.com",
        "mode": "url_query",
        "supports_image_paste": False,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "google_translate_vi",
        "name": "Google Translate (Auto -> VI)",
        "keywords": "translate dich google translate tieng viet english",
        "url_template": "https://translate.google.com/?sl=auto&tl=vi&text={text}&op=translate",
        "base_url": "https://translate.google.com",
        "mode": "url_query",
        "supports_image_paste": False,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "youtube_search",
        "name": "YouTube Search",
        "keywords": "youtube video tim kiem nhac",
        "url_template": "https://www.youtube.com/results?search_query={text}",
        "base_url": "https://www.youtube.com",
        "mode": "url_query",
        "supports_image_paste": False,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "gemini",
        "name": "Google Gemini (AI - Paste Text / Image)",
        "keywords": "gemini google ai bard prompt anh image paste",
        "url_template": "https://gemini.google.com/app",
        "base_url": "https://gemini.google.com/app",
        "mode": "paste_submit",
        "supports_image_paste": True,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "chatgpt",
        "name": "ChatGPT (OpenAI)",
        "keywords": "chatgpt openai gpt ai prompt anh image",
        "url_template": "https://chatgpt.com/?q={text}",
        "base_url": "https://chatgpt.com",
        "mode": "url_query",
        "supports_image_paste": True,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "claude",
        "name": "Claude (Anthropic)",
        "keywords": "claude anthropic ai prompt anh image",
        "url_template": "https://claude.ai/new?q={text}",
        "base_url": "https://claude.ai/new",
        "mode": "url_query",
        "supports_image_paste": True,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "copilot",
        "name": "Microsoft Copilot",
        "keywords": "copilot microsoft bing ai prompt anh image",
        "url_template": "https://copilot.microsoft.com/?q={text}",
        "base_url": "https://copilot.microsoft.com",
        "mode": "url_query",
        "supports_image_paste": True,
        "default_prompt": "",
        "auto_submit": True,
    },
    {
        "id": "perplexity",
        "name": "Perplexity AI",
        "keywords": "perplexity ai search hoi dap",
        "url_template": "https://www.perplexity.ai/search?q={text}",
        "base_url": "https://www.perplexity.ai",
        "mode": "url_query",
        "supports_image_paste": True,
        "default_prompt": "",
        "auto_submit": True,
    },
]


def search_webclip_templates(query: str = "") -> list[dict[str, Any]]:
    """Search WebClip templates by name and keywords."""
    clean_q = _fold_ascii(query.strip())
    if not clean_q:
        return [dict(t) for t in BUILTIN_WEBCLIP_TEMPLATES]

    tokens = clean_q.split()
    results: list[dict[str, Any]] = []
    for t in BUILTIN_WEBCLIP_TEMPLATES:
        haystack = _fold_ascii(f"{t['name']} {t.get('keywords', '')}")
        if all(tok in haystack for tok in tokens):
            results.append(dict(t))
    return results
