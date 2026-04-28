"""Pre-compute SimCSE (Seznam/simcse-small-e-czech) embeddings for the vocab.

Encodes both:
- noun lemmas in vocab.json (these dominate ranking)
- common forms from embeddings_index.json (so already-known fastText words also have a SimCSE vector for OOV-free lookup)

Output: data/embeddings_simcse.npz, data/embeddings_simcse_index.json.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MODEL_NAME = "Seznam/simcse-small-e-czech"
OUT_NPZ = DATA / "embeddings_simcse.npz"
OUT_INDEX = DATA / "embeddings_simcse_index.json"


def main() -> None:
    fasttext_idx = json.loads((DATA / "embeddings_index.json").read_text())
    words = list(fasttext_idx.keys())
    print(f"Encoding {len(words)} words with {MODEL_NAME}", flush=True)

    print("Loading model…", flush=True)
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"  loaded in {time.time()-t0:.1f}s", flush=True)

    t0 = time.time()
    vecs = model.encode(
        words,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)
    print(f"  encoded in {time.time()-t0:.1f}s, shape={vecs.shape}", flush=True)

    np.savez_compressed(OUT_NPZ, words=np.array(words), vectors=vecs)
    OUT_INDEX.write_text(json.dumps({w: i for i, w in enumerate(words)}, ensure_ascii=False))
    print(f"Wrote {OUT_NPZ} and {OUT_INDEX}", flush=True)


if __name__ == "__main__":
    main()
