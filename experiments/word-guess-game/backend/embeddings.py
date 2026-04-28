"""Embedding store + ranking + lemmatization for the guessing game.

Supports two embedding models side-by-side:
- "fasttext"  — pre-computed cc.cs.300 (lookup only, no inference)
- "simcse"    — Seznam/simcse-small-e-czech (sentence-transformer, can encode OOV at runtime)

Both share the same noun-vocab list (from data/vocab.json) and the same lemmatization
cache (from UDPipe). Each provides its own vector matrix.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from threading import Lock

import httpx
import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"
WORD_RE = re.compile(r"^[a-záčďéěíňóřšťúůýž]{2,25}$")

UDPIPE_URL = "https://lindat.mff.cuni.cz/services/udpipe/api/process"
UDPIPE_MODEL = "czech"

SIMCSE_MODEL_NAME = "Seznam/simcse-small-e-czech"


class _Provider:
    """Holds vectors + index + the noun-vocab subview for one embedding model."""

    name: str
    words: list[str]
    vectors: np.ndarray  # (N, D), L2-normalized
    index: dict[str, int]
    vocab_lemmas: list[str]
    vocab_vectors: np.ndarray  # (V, D)
    vocab_idx: dict[str, int]

    def vector_for(self, word: str, lemma: str) -> tuple[str, np.ndarray | None]:
        """Subclasses override to add OOV-encoding behaviour."""
        if word in self.index:
            return word, self.vectors[self.index[word]]
        if lemma in self.index:
            return lemma, self.vectors[self.index[lemma]]
        return lemma, None

    def rank_in_vocab(self, target_lemma: str, guess_word: str) -> int | None:
        if target_lemma not in self.vocab_idx or guess_word not in self.vocab_idx:
            return None
        target_vec = self.vocab_vectors[self.vocab_idx[target_lemma]]
        sims = self.vocab_vectors @ target_vec
        order = np.argsort(-sims)
        guess_row = self.vocab_idx[guess_word]
        return int(np.where(order == guess_row)[0][0]) + 1


class _StaticProvider(_Provider):
    """Pure lookup, no runtime encoding. (fastText path.)"""

    def __init__(self, name: str, npz_path: Path, index_path: Path, vocab_lemmas: list[str]) -> None:
        npz = np.load(npz_path, allow_pickle=True)
        self.name = name
        self.words = list(npz["words"])
        self.vectors = npz["vectors"].astype(np.float32)
        self.index = json.loads(index_path.read_text())
        self.vocab_lemmas = [w for w in vocab_lemmas if w in self.index]
        rows = np.array([self.index[w] for w in self.vocab_lemmas])
        self.vocab_vectors = self.vectors[rows]
        self.vocab_idx = {w: i for i, w in enumerate(self.vocab_lemmas)}


class _TransformerProvider(_Provider):
    """Sentence-Transformer model. Has a static cache + can encode OOV inputs."""

    def __init__(
        self,
        name: str,
        npz_path: Path,
        index_path: Path,
        vocab_lemmas: list[str],
        model_name: str,
    ) -> None:
        npz = np.load(npz_path, allow_pickle=True)
        self.name = name
        self.words = list(npz["words"])
        self.vectors = npz["vectors"].astype(np.float32)
        self.index = json.loads(index_path.read_text())
        self.vocab_lemmas = [w for w in vocab_lemmas if w in self.index]
        rows = np.array([self.index[w] for w in self.vocab_lemmas])
        self.vocab_vectors = self.vectors[rows]
        self.vocab_idx = {w: i for i, w in enumerate(self.vocab_lemmas)}

        # Lazy-load the model only on first OOV encode.
        self._model_name = model_name
        self._model = None
        self._encode_lock = Lock()

    def _ensure_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def vector_for(self, word: str, lemma: str) -> tuple[str, np.ndarray | None]:
        # Same lookup path as static.
        for candidate in (word, lemma):
            if candidate in self.index:
                return candidate, self.vectors[self.index[candidate]]
        # Try live encoding.
        try:
            with self._encode_lock:
                model = self._ensure_model()
                vec = model.encode(
                    [lemma],
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                )[0].astype(np.float32)
            return lemma, vec
        except Exception:
            return lemma, None


class EmbeddingHub:
    """Top-level container holding both model providers + shared lemmatization."""

    def __init__(self) -> None:
        vocab_records = json.loads((DATA / "vocab.json").read_text())
        all_lemmas = [r["lemma"] for r in vocab_records]
        self.vocab_freq = {r["lemma"]: r["freq"] for r in vocab_records}

        self.providers: dict[str, _Provider] = {}
        self.providers["fasttext"] = _StaticProvider(
            "fasttext",
            DATA / "embeddings.npz",
            DATA / "embeddings_index.json",
            all_lemmas,
        )

        sc_npz = DATA / "embeddings_simcse.npz"
        sc_index = DATA / "embeddings_simcse_index.json"
        if sc_npz.exists() and sc_index.exists():
            self.providers["simcse"] = _TransformerProvider(
                "simcse",
                sc_npz,
                sc_index,
                all_lemmas,
                SIMCSE_MODEL_NAME,
            )

        # Targets: only those covered by our default model (fastText).
        ft = self.providers["fasttext"]
        self.targets: list[str] = [
            w for w in json.loads((DATA / "target_words.json").read_text())
            if w in ft.vocab_idx
            and (
                "simcse" not in self.providers
                or w in self.providers["simcse"].vocab_idx
            )
        ]

        # UDPipe cache.
        cache_path = DATA / "udpipe_cache.json"
        self._lemma_cache: dict[str, str] = {}
        if cache_path.exists():
            for form, (lemma, _upos) in json.loads(cache_path.read_text()).items():
                self._lemma_cache[form] = lemma
        self._lemma_cache_lock = Lock()
        self._http = httpx.Client(timeout=10.0)

    # ---- accessors ----

    def get(self, model: str) -> _Provider:
        if model not in self.providers:
            return self.providers["fasttext"]
        return self.providers[model]

    def available_models(self) -> list[str]:
        return list(self.providers.keys())

    def vocab_size(self, model: str = "fasttext") -> int:
        return len(self.get(model).vocab_lemmas)

    # ---- lemmatization (shared across models) ----

    def normalize(self, raw: str) -> str:
        return raw.strip().lower()

    def lemmatize(self, word: str) -> str:
        word = self.normalize(word)
        if word in self._lemma_cache:
            return self._lemma_cache[word]
        try:
            resp = self._http.post(
                UDPIPE_URL,
                data={"tokenizer": "", "tagger": "", "model": UDPIPE_MODEL, "data": word},
            )
            resp.raise_for_status()
            for line in resp.json()["result"].splitlines():
                if not line or line.startswith("#"):
                    continue
                cols = line.split("\t")
                if len(cols) >= 4 and "-" not in cols[0] and "." not in cols[0]:
                    lemma = cols[2].lower()
                    with self._lemma_cache_lock:
                        self._lemma_cache[word] = lemma
                    return lemma
        except Exception:
            pass
        return word

    def vector_for(self, word: str, model: str) -> tuple[str, np.ndarray | None]:
        norm = self.normalize(word)
        lem = self.lemmatize(norm)
        return self.get(model).vector_for(norm, lem)
