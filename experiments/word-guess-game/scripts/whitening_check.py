"""Empirically measure anisotropy and whitening's effect on our embeddings.

For each model (fastText, SimCSE):
  1. Anisotropy: mean cosine sim of random unrelated pairs.
  2. Signal: mean cosine sim between each word and its top-10 nearest neighbours.
  3. SNR: (signal - anisotropy_baseline) / std_baseline → discrimination quality.
  4. Hand-picked qualitative pairs (semantically close vs. unrelated).

Run before vs. after BERT-whitening (center + rotate-by-PCA + scale-to-unit-var
+ re-normalize).  Optionally also a truncated whitening keeping only top-k axes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"


def load_provider(npz_name: str, idx_name: str):
    npz = np.load(DATA / npz_name, allow_pickle=True)
    idx = json.loads((DATA / idx_name).read_text())
    return list(npz["words"]), npz["vectors"].astype(np.float32), idx


def normalize(vecs: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(vecs, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return vecs / n


def whiten_transform(vecs: np.ndarray, k: int | None = None):
    """Returns (mean, W) such that x' = (x - mean) @ W is whitened.
    If ``k`` is given, keep only top-k principal components."""
    mu = vecs.mean(axis=0, keepdims=True)
    centered = vecs - mu
    cov = (centered.T @ centered) / (centered.shape[0] - 1)
    eigvals, eigvecs = np.linalg.eigh(cov)  # ascending
    order = np.argsort(-eigvals)            # descending
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    if k is not None:
        eigvals = eigvals[:k]
        eigvecs = eigvecs[:, :k]
    eigvals = np.maximum(eigvals, 1e-12)
    W = eigvecs @ np.diag(1.0 / np.sqrt(eigvals))
    return mu.astype(np.float32), W.astype(np.float32)


def apply_whitening(vecs: np.ndarray, mu: np.ndarray, W: np.ndarray) -> np.ndarray:
    out = (vecs - mu) @ W
    return normalize(out)


def anisotropy(vecs: np.ndarray, n_pairs: int = 50_000, rng=None) -> tuple[float, float]:
    rng = rng or np.random.default_rng(42)
    N = vecs.shape[0]
    a = rng.integers(0, N, size=n_pairs)
    b = rng.integers(0, N, size=n_pairs)
    mask = a != b
    a, b = a[mask], b[mask]
    sims = np.einsum("ij,ij->i", vecs[a], vecs[b])
    return float(sims.mean()), float(sims.std())


def topk_neighbour_sim(vecs: np.ndarray, sample_size: int = 1500, k: int = 10, rng=None) -> float:
    """For a sample of words, mean cosine to their top-k nearest neighbours
    (excluding self). Higher = the model groups similar things together."""
    rng = rng or np.random.default_rng(7)
    N = vecs.shape[0]
    idx = rng.choice(N, size=min(sample_size, N), replace=False)
    sample = vecs[idx]                       # (S, D)
    sims = sample @ vecs.T                   # (S, N)
    # mask out self
    for i, gi in enumerate(idx):
        sims[i, gi] = -np.inf
    # top-k mean
    part = np.partition(-sims, k, axis=1)[:, :k]
    return float((-part).mean())


def qualitative_pairs(words: list[str], idx: dict[str, int], vecs: np.ndarray, pairs: list[tuple[str, str]]) -> list[tuple[str, str, float]]:
    out = []
    for a, b in pairs:
        if a not in idx or b not in idx:
            out.append((a, b, float("nan")))
            continue
        sim = float(vecs[idx[a]] @ vecs[idx[b]])
        out.append((a, b, sim))
    return out


def report(name: str, vecs: np.ndarray, idx: dict[str, int], pairs: list[tuple[str, str]]) -> None:
    aniso_mean, aniso_std = anisotropy(vecs)
    sig = topk_neighbour_sim(vecs)
    snr = (sig - aniso_mean) / max(aniso_std, 1e-9)
    print(f"  anisotropy  mean cosine of random pairs : {aniso_mean:+.3f}  ± {aniso_std:.3f}")
    print(f"  signal      mean cosine to top-10 NN     : {sig:+.3f}")
    print(f"  SNR         (signal - baseline) / std    : {snr:.2f}")
    print(f"  qualitative pairs:")
    for a, b, s in qualitative_pairs(list(idx.keys()), idx, vecs, pairs):
        print(f"      {a:>14} ↔ {b:<14}  cos = {s:+.3f}")


PAIRS = [
    ("kočka", "pes"),         # both animals — should be HIGH
    ("kočka", "matematika"),  # unrelated — should be LOW
    ("auto", "banán"),        # unrelated — should be LOW
    ("láska", "nenávist"),    # antonyms but co-occur — expect anisotropy spike
    ("král", "královna"),     # same domain, gendered — should be HIGH
    ("strom", "les"),         # part-of — should be HIGH
    ("ruka", "noha"),         # body parts — should be HIGH
    ("voda", "oheň"),         # elements, opposing — interesting
    ("počítač", "klávesnice"),# tool relation — should be HIGH
    ("ředitel", "polévka"),   # unrelated — should be LOW
]


def run_for(name: str, npz: str, idx_file: str) -> None:
    print("=" * 78)
    print(f"  {name}")
    print("=" * 78)
    _, vecs, idx = load_provider(npz, idx_file)
    vecs = normalize(vecs)

    print(f"\n[{name}] BEFORE whitening (shape {vecs.shape}):")
    report(name, vecs, idx, PAIRS)

    mu, W = whiten_transform(vecs)
    vecs_w = apply_whitening(vecs, mu, W)
    print(f"\n[{name}] AFTER full whitening (shape {vecs_w.shape}):")
    report(name, vecs_w, idx, PAIRS)

    # Truncated whitening (BERT-whitening keeps top-k components).
    for k in (128, 64):
        if k >= vecs.shape[1]:
            continue
        mu, W = whiten_transform(vecs, k=k)
        vecs_t = apply_whitening(vecs, mu, W)
        print(f"\n[{name}] AFTER whitening + truncate to top-{k} components (shape {vecs_t.shape}):")
        report(name, vecs_t, idx, PAIRS)


def main() -> None:
    run_for("fastText cc.cs.300", "embeddings.npz", "embeddings_index.json")
    run_for("SimCSE small e-czech", "embeddings_simcse.npz", "embeddings_simcse_index.json")


if __name__ == "__main__":
    main()
