"""Turns email text into a fixed-size vector. The extension has an identical TypeScript copy
(extension/src/shared/featurize.ts): both MUST produce the same numbers, or the model breaks.

Method: hashing trick. Each word, word pair and 4-character piece of a word is hashed (FNV-1a)
into one of DIM buckets, counts are log-scaled, and the vector is L2-normalised. No vocabulary
file is needed. The character pieces let "urgent", "urgently" and "urgency" share features.
"""
import math
import re

DIM = 4096
TOKEN_RE = re.compile(r"[a-z0-9]+")


def fnv1a(text: str) -> int:
    h = 0x811C9DC5
    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def tokens(text: str) -> list[str]:
    words = TOKEN_RE.findall(text.lower())
    out = words + [f"{a}_{b}" for a, b in zip(words, words[1:])]
    for w in words:
        w = f"<{w}>"  # mark word boundaries so prefixes/suffixes are distinct
        out += [w[i:i + 4] for i in range(max(1, len(w) - 3))]
    return out


def sparse_features(text: str) -> dict[int, float]:
    """Non-zero entries only: {bucket: value}. Fast, and what training uses."""
    counts: dict[int, float] = {}
    for tok in tokens(text):
        k = fnv1a(tok) % DIM
        counts[k] = counts.get(k, 0.0) + 1.0
    logged = {k: math.log1p(x) for k, x in counts.items()}
    norm = math.sqrt(sum(x * x for x in logged.values()))
    return {k: x / norm for k, x in logged.items()} if norm else logged


def featurize(text: str) -> list[float]:
    v = [0.0] * DIM
    for k, x in sparse_features(text).items():
        v[k] = x
    return v


def email_text(subject: str, body: str) -> str:
    return f"{subject} {subject} {body}"  # subject counted twice: it's the strongest signal
