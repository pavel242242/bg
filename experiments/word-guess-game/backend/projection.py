"""2D projections for the visualizations.

- circles_layout: PCA on (target + guesses), recentered so target is at origin.
  We then *override* the radial distance with the actual cosine distance to target,
  keeping only the angular information from PCA. This guarantees that "rings"
  (similarity bands) are visually meaningful.

- starry_sky_layout: UMAP on (target + guesses) → free 2D layout. Edges are an
  MST connecting all guesses (forms a constellation that hints at clusters).
"""

from __future__ import annotations

import math

import numpy as np
from sklearn.decomposition import PCA


def circles_layout(target_vec: np.ndarray, guess_vecs: list[np.ndarray]) -> dict:
    """Return positions for the concentric-circles viz.

    Output:
      {
        "target": [0, 0],
        "guesses": [{ "x": float, "y": float, "sim": float, "dist": float }, ...]
      }
    Distance from origin = (1 - cosine_similarity), in range ~[0, 2].
    Angle is determined by 2-D PCA over the cohort of guesses.
    """
    if not guess_vecs:
        return {"target": [0.0, 0.0], "guesses": []}

    # Cosine similarity (vectors are L2-normed).
    sims = np.array([float(np.dot(g, target_vec)) for g in guess_vecs], dtype=np.float32)
    dists = 1.0 - sims  # 0 = identical, 2 = opposite

    if len(guess_vecs) == 1:
        # Single guess: place along x-axis.
        return {
            "target": [0.0, 0.0],
            "guesses": [{"x": float(dists[0]), "y": 0.0, "sim": float(sims[0]), "dist": float(dists[0])}],
        }

    # Compute PCA over (target + guesses) to get a stable angle for each guess.
    cohort = np.stack([target_vec] + list(guess_vecs))
    n_components = min(2, cohort.shape[0] - 1, cohort.shape[1])
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(cohort)
    if coords.shape[1] == 1:
        coords = np.column_stack([coords, np.zeros(coords.shape[0])])
    target_pc = coords[0]
    guess_pcs = coords[1:]
    rel = guess_pcs - target_pc  # vectors from target to each guess in PCA space

    out = []
    for i, r in enumerate(rel):
        angle = math.atan2(float(r[1]), float(r[0])) if (r[0] != 0 or r[1] != 0) else 0.0
        d = float(dists[i])
        out.append({
            "x": d * math.cos(angle),
            "y": d * math.sin(angle),
            "sim": float(sims[i]),
            "dist": d,
        })
    return {"target": [0.0, 0.0], "guesses": out}


def starry_sky_layout(target_vec: np.ndarray, guess_vecs: list[np.ndarray]) -> dict:
    """UMAP projection of target + guesses to 2D, with MST constellation edges.

    Returns:
      {
        "target": [x, y],
        "guesses": [{ "x", "y", "sim" }, ...],
        "edges": [[i, j], ...],   # indices into guesses list
      }
    """
    if not guess_vecs:
        return {"target": [0.0, 0.0], "guesses": [], "edges": []}

    sims = np.array([float(np.dot(g, target_vec)) for g in guess_vecs], dtype=np.float32)
    cohort = np.stack([target_vec] + list(guess_vecs)).astype(np.float32)

    if cohort.shape[0] < 4:
        # UMAP needs more data. Fall back to PCA 2D.
        n_components = min(2, cohort.shape[0] - 1, cohort.shape[1])
        if n_components < 1:
            return {"target": [0.0, 0.0], "guesses": [], "edges": []}
        pca = PCA(n_components=n_components)
        coords = pca.fit_transform(cohort)
        if coords.shape[1] == 1:
            coords = np.column_stack([coords, np.zeros(coords.shape[0])])
    else:
        # Defer the UMAP import: it's slow to import.
        import umap

        n_neighbors = min(15, cohort.shape[0] - 1)
        reducer = umap.UMAP(
            n_components=2,
            n_neighbors=n_neighbors,
            min_dist=0.3,
            metric="cosine",
            random_state=42,
        )
        coords = reducer.fit_transform(cohort)

    # Re-center so target is at origin.
    coords = coords - coords[0]

    target_pos = coords[0].tolist()
    guess_pos = coords[1:]

    # MST over guess positions (using full embedding distances, not 2D).
    edges = _mst_edges(np.stack(guess_vecs))

    return {
        "target": [float(target_pos[0]), float(target_pos[1])],
        "guesses": [
            {"x": float(guess_pos[i, 0]), "y": float(guess_pos[i, 1]), "sim": float(sims[i])}
            for i in range(guess_pos.shape[0])
        ],
        "edges": edges,
    }


def _mst_edges(vecs: np.ndarray) -> list[list[int]]:
    """Prim's algorithm on cosine-distance graph; returns list of [i, j] edges."""
    n = vecs.shape[0]
    if n < 2:
        return []
    sims = vecs @ vecs.T
    dist = 1.0 - sims
    np.fill_diagonal(dist, np.inf)

    in_tree = [False] * n
    in_tree[0] = True
    min_dist = dist[0].copy()
    parent = [0] * n
    edges: list[list[int]] = []

    for _ in range(n - 1):
        best = -1
        best_d = float("inf")
        for v in range(n):
            if not in_tree[v] and min_dist[v] < best_d:
                best_d = float(min_dist[v])
                best = v
        if best < 0:
            break
        in_tree[best] = True
        edges.append(sorted([parent[best], best]))
        for v in range(n):
            if not in_tree[v] and dist[best, v] < min_dist[v]:
                min_dist[v] = float(dist[best, v])
                parent[v] = best

    return edges
