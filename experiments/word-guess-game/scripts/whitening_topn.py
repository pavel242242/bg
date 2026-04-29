"""Compare top-N nearest neighbours BEFORE vs AFTER whitening.

This is what actually matters for the game: ranking.  Anisotropy doesn't just
inflate cosine values — it can also pollute the *order* of nearest neighbours,
because the dominant shared direction acts like a constant offset that pulls
high-norm-projection words to the top regardless of semantic similarity.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"


def load(npz_name: str, idx_name: str):
    npz = np.load(DATA / npz_name, allow_pickle=True)
    idx = json.loads((DATA / idx_name).read_text())
    return list(npz["words"]), npz["vectors"].astype(np.float32), idx


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return v / n


def whiten(vecs: np.ndarray, k: int | None = None):
    mu = vecs.mean(axis=0, keepdims=True)
    centered = vecs - mu
    cov = (centered.T @ centered) / (centered.shape[0] - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(-eigvals)
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    if k is not None:
        eigvals = eigvals[:k]
        eigvecs = eigvecs[:, :k]
    eigvals = np.maximum(eigvals, 1e-12)
    W = eigvecs @ np.diag(1.0 / np.sqrt(eigvals))
    return normalize((vecs - mu) @ W)


def topn(target: str, words: list[str], idx: dict[str, int], vecs: np.ndarray, n: int = 10) -> list[tuple[str, float]]:
    if target not in idx:
        return []
    t = vecs[idx[target]]
    sims = vecs @ t
    sims[idx[target]] = -np.inf  # exclude self
    top = np.argpartition(-sims, n)[:n]
    top = top[np.argsort(-sims[top])]
    return [(words[i], float(sims[i])) for i in top]


def show(name: str, npz: str, idx_file: str, targets: list[str]) -> None:
    print("=" * 78)
    print(f"  {name}")
    print("=" * 78)
    words, vecs, idx = load(npz, idx_file)
    vecs_b = normalize(vecs)
    vecs_w = whiten(vecs_b)
    vecs_t = whiten(vecs_b, k=128)

    for target in targets:
        if target not in idx:
            print(f"\n>>> {target!r}: not in vocab")
            continue
        print(f"\n>>> Top-10 nearest neighbours of {target!r}")
        print(f"    {'BEFORE':<35} {'WHITENED':<35} {'WHITENED top-128'}")
        before = topn(target, words, idx, vecs_b)
        after  = topn(target, words, idx, vecs_w)
        trunc  = topn(target, words, idx, vecs_t)
        for a, b, c in zip(before, after, trunc):
            print(f"    {a[0]:<14} {a[1]:+.3f}      "
                  f"{b[0]:<14} {b[1]:+.3f}      "
                  f"{c[0]:<14} {c[1]:+.3f}")


TARGETS = ["kočka", "letadlo", "obloha", "polévka", "matematika", "vražda", "pampeliška"]


def main() -> None:
    show("fastText cc.cs.300", "embeddings.npz", "embeddings_index.json", TARGETS)
    show("SimCSE small e-czech", "embeddings_simcse.npz", "embeddings_simcse_index.json", TARGETS)


if __name__ == "__main__":
    main()
