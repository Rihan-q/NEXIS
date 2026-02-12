# ============================================================
#  brain/knowledge.py — Wikipedia & DuckDuckGo search
#  Uses only free, open-source libraries. No API keys needed.
# ============================================================

import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

# ── Optional imports with graceful fallbacks ─────────────────
try:
    import wikipedia
    WIKIPEDIA_OK = True
except ImportError:
    WIKIPEDIA_OK = False
    print("[WARN] 'wikipedia' not installed. Run: pip install wikipedia-api")

try:
    from duckduckgo_search import DDGS
    DDG_OK = True
except ImportError:
    DDG_OK = False
    print("[WARN] 'duckduckgo_search' not installed. Run: pip install duckduckgo-search")

try:
    import requests
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False


def _trim(text: str, max_sentences: int = config.ANSWER_MAX_SENTENCES) -> str:
    """Keep only the first `max_sentences` sentences of `text`."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    trimmed   = " ".join(sentences[:max_sentences])
    return trimmed if trimmed else text[:300]


# ── Wikipedia search ─────────────────────────────────────────
def search_wikipedia(query: str) -> str | None:
    """
    Search Wikipedia for `query`.
    Returns a short 2-sentence summary, or None on failure.
    """
    if not WIKIPEDIA_OK:
        return None
    try:
        wikipedia.set_lang("en")
        # search() returns page title candidates
        results = wikipedia.search(query, results=3)
        if not results:
            return None

        # Try each candidate until we get a valid page
        for title in results:
            try:
                page    = wikipedia.page(title, auto_suggest=False)
                summary = wikipedia.summary(title, sentences=config.WIKIPEDIA_SENTENCES, auto_suggest=False)
                return _trim(summary)
            except wikipedia.exceptions.DisambiguationError as e:
                # Grab the first specific option
                if e.options:
                    try:
                        summary = wikipedia.summary(e.options[0], sentences=config.WIKIPEDIA_SENTENCES, auto_suggest=False)
                        return _trim(summary)
                    except Exception:
                        continue
            except wikipedia.exceptions.PageError:
                continue
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"[Wikipedia] Error: {e}")
        return None


# ── DuckDuckGo search ─────────────────────────────────────────
def search_duckduckgo(query: str) -> str | None:
    """
    Search DuckDuckGo using the duckduckgo_search library (free, no key).
    Returns the best snippet found, trimmed to 2 sentences.
    Falls back to HTML scraping if the library is missing.
    """
    if DDG_OK:
        return _ddg_library(query)
    elif BS4_OK:
        return _ddg_scrape(query)
    else:
        return None


def _ddg_library(query: str) -> str | None:
    """Use the `duckduckgo_search` library for clean JSON results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results = config.DDG_MAX_RESULTS,
                region      = "wt-wt",
                safesearch  = "moderate",
            ))
        if not results:
            return None
        # Combine body snippets from top results
        snippets = [r.get("body", "") for r in results if r.get("body")]
        if not snippets:
            return None
        combined = " ".join(snippets[:2])
        return _trim(combined)
    except Exception as e:
        print(f"[DDG] Library error: {e}")
        return None


def _ddg_scrape(query: str) -> str | None:
    """
    HTML-scrape fallback: parse DuckDuckGo Lite (no JS needed).
    Used only if duckduckgo_search is not installed.
    """
    try:
        url     = "https://lite.duckduckgo.com/lite/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        params  = {"q": query}
        resp    = requests.post(url, data=params, headers=headers, timeout=8)
        soup    = BeautifulSoup(resp.text, "html.parser")
        # DDG Lite stores result snippets in <td class="result-snippet">
        snippets = [td.get_text(strip=True) for td in soup.select("td.result-snippet")]
        if not snippets:
            # Broader fallback: grab all paragraph-like text
            snippets = [p.get_text(strip=True) for p in soup.find_all("td") if len(p.get_text(strip=True)) > 60]
        if snippets:
            return _trim(" ".join(snippets[:2]))
        return None
    except Exception as e:
        print(f"[DDG-scrape] Error: {e}")
        return None


# ── Unified search entry point ────────────────────────────────
def find_answer(query: str, prefer_wikipedia: bool = True) -> str:
    """
    Main search function used by the brain.

    Strategy:
    1. If `prefer_wikipedia=True`  → try Wikipedia first; DDG as fallback.
    2. If `prefer_wikipedia=False` → try DDG first; Wikipedia as fallback.
    3. If both fail → honest "I don't know" message.
    """
    if prefer_wikipedia:
        answer = search_wikipedia(query) or search_duckduckgo(query)
    else:
        answer = search_duckduckgo(query) or search_wikipedia(query)

    if answer:
        return answer
    return "I couldn't find a reliable answer for that. Try asking me something else!"
