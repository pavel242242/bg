"""Extract a compact subset of fastText cc.cs.300 vectors for our game.

We keep:
- All noun lemmas from data/vocab.json (these are the "vocabulary" that ranks tips).
- All forms from data/cs_50k_raw.txt that match our orthography filter
  (useful for embedding non-lemmatized user input directly).

Output: data/embeddings.npz with arrays:
  - words: list[str] of length N
  - vectors: float32 array (N, 300), L2-normalized for fast cosine via dot.
And data/embeddings_index.json: dict[word -> int] for fast lookup.
"""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VEC_GZ = ROOT / "data" / "cc.cs.300.vec.gz"
VOCAB = ROOT / "data" / "vocab.json"
RAW = ROOT / "data" / "cs_50k_raw.txt"
OUT_NPZ = ROOT / "data" / "embeddings.npz"
OUT_INDEX = ROOT / "data" / "embeddings_index.json"

WORD_RE = re.compile(r"^[a-záčďéěíňóřšťúůýž]{2,25}$")


def load_keep_set() -> set[str]:
    keep: set[str] = set()
    for r in json.loads(VOCAB.read_text()):
        keep.add(r["lemma"])
    with RAW.open() as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            w = parts[0].lower()
            if WORD_RE.match(w):
                keep.add(w)
    print(f"Targeting {len(keep)} word forms", flush=True)
    return keep


def main() -> None:
    keep = load_keep_set()
    found_words: list[str] = []
    found_vectors: list[np.ndarray] = []

    with gzip.open(VEC_GZ, "rt", encoding="utf-8") as f:
        header = f.readline().split()
        total, dim = int(header[0]), int(header[1])
        print(f"fastText file: {total} words, {dim} dim", flush=True)
        seen = 0
        for line in f:
            seen += 1
            if seen % 200000 == 0:
                print(f"  scanned {seen}/{total}, kept {len(found_words)}", flush=True)
            sp = line.rstrip("\n").split(" ")
            word = sp[0]
            if word not in keep:
                continue
            try:
                vec = np.array([float(x) for x in sp[1 : dim + 1]], dtype=np.float32)
            except ValueError:
                continue
            if vec.shape[0] != dim:
                continue
            n = np.linalg.norm(vec)
            if n == 0:
                continue
            found_words.append(word)
            found_vectors.append(vec / n)

    arr = np.stack(found_vectors).astype(np.float32)
    np.savez_compressed(OUT_NPZ, words=np.array(found_words), vectors=arr)
    OUT_INDEX.write_text(json.dumps({w: i for i, w in enumerate(found_words)}, ensure_ascii=False))
    print(f"Wrote {OUT_NPZ}: {arr.shape[0]} vectors x {arr.shape[1]} dim", flush=True)
    print(f"Wrote {OUT_INDEX}", flush=True)
    print(f"Coverage: {len(found_words)}/{len(keep)} = {len(found_words)/len(keep):.1%}", flush=True)


if __name__ == "__main__":
    main()
