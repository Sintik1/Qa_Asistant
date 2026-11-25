"""Lexical overlap for chat ranking.

Hash embeddings do not match meaning, so a chunk about a router installment can
outrank the page that actually names the subject. Shared word stems put that
page first and drop unrelated fragments.
"""

from __future__ import annotations

import re

# Latin acronyms such as SDP are 3 letters. Cyrillic words start at 4.
_TOKEN_RE = re.compile(r"[A-Za-z]{3,}|[0-9А-Яа-яЁё]{4,}|[A-Za-zА-Яа-яЁё0-9]{4,}")
_STOP = frozenset(
    {
        "какой",
        "какая",
        "какие",
        "какое",
        "каким",
        "какую",
        "этого",
        "этому",
        "этом",
        "также",
        "есть",
        "можно",
        "нужно",
        "надо",
        "этот",
        "эта",
        "эти",
        "того",
        "только",
        "если",
        "или",
        "что",
    }
)


def _tokens(text: str) -> list[str]:
    found: list[str] = []
    for token in _TOKEN_RE.findall(text or ""):
        word = token.lower().replace("ё", "е")
        if word not in _STOP:
            found.append(word)
    return found


def _pair_score(left: str, right: str) -> int:
    """Exact word scores higher than the same word with a different ending."""
    if left == right:
        return 3
    shared = 0
    for a, b in zip(left, right):
        if a != b:
            break
        shared += 1
    shorter = min(len(left), len(right))
    # «подключении» / «подключения» share a long stem.
    # «активатор» / «активна» share only «актив» and must not match.
    if shared >= 6 and shared >= shorter - 3:
        return 1
    return 0


def query_stems(text: str) -> set[str]:
    return set(_tokens(text))


def lexical_overlap(query: str, *parts: str | None) -> int:
    needles = _tokens(query)
    if not needles:
        return 0
    haystack = _tokens(" ".join(part or "" for part in parts))
    if not haystack:
        return 0
    total = 0
    for needle in needles:
        total += max(_pair_score(needle, word) for word in haystack)
    return total
