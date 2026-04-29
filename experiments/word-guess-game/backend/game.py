"""Game state + session management."""

from __future__ import annotations

import random
import secrets
import time
from dataclasses import dataclass, field

import numpy as np

from .embeddings import EmbeddingHub
from .projection import circles_layout, starry_sky_layout


@dataclass
class Guess:
    word: str          # the resolved word (lemma if we lemmatized)
    raw: str           # what the user typed
    sim: float         # cosine similarity for the active model
    rank: int | None   # 1-based rank in vocab; None if OOV
    ts: float
    fallback: bool = False  # True ⇒ sim came from SimCSE fallback (active model didn't have the word)


@dataclass
class Game:
    id: str
    target: str
    model: str         # "fasttext" or "simcse"
    started_at: float
    guesses: list[Guess] = field(default_factory=list)
    solved: bool = False


class GameManager:
    """In-memory store of active games."""

    def __init__(self, hub: EmbeddingHub) -> None:
        self.hub = hub
        self.games: dict[str, Game] = {}

    def new_game(self, seed: str | None = None, model: str = "fasttext") -> Game:
        if model not in self.hub.providers:
            model = "fasttext"
        rnd = random.Random(seed) if seed else random.Random()
        target = rnd.choice(self.hub.targets)
        gid = secrets.token_urlsafe(8)
        game = Game(id=gid, target=target, model=model, started_at=time.time())
        self.games[gid] = game
        return game

    def get(self, game_id: str) -> Game | None:
        return self.games.get(game_id)

    def submit_guess(self, game: Game, raw_word: str) -> dict:
        norm = self.hub.normalize(raw_word)
        lemma = self.hub.lemmatize(norm)

        resolved, sim, rank, fallback = self._score_guess(game, norm, lemma)

        if resolved is None:
            return {
                "ok": False,
                "error": "unknown_word",
                "message": (
                    f'Slovo „{raw_word}" neznám. '
                    "Zkus podstatné jméno v 1. pádě, nebo přepni na SimCSE."
                ),
            }

        if any(g.word == resolved for g in game.guesses):
            existing = next(g for g in game.guesses if g.word == resolved)
            return {
                "ok": True,
                "duplicate": True,
                "guess": _guess_to_dict(existing),
                **self._snapshot(game),
            }

        guess = Guess(
            word=resolved,
            raw=raw_word.strip(),
            sim=sim,
            rank=rank,
            ts=time.time(),
            fallback=fallback,
        )
        game.guesses.append(guess)

        if not fallback and resolved == game.target:
            game.solved = True

        return {
            "ok": True,
            "duplicate": False,
            "guess": _guess_to_dict(guess),
            **self._snapshot(game),
        }

    def _score_guess(
        self, game: Game, norm: str, lemma: str
    ) -> tuple[str | None, float, int | None, bool]:
        """Resolve a guess to (word, sim, rank, fallback). word=None if we couldn't score it.

        Tries the active model first; if it can't find the word, falls back to SimCSE
        (live encoding) so that any word the user types still gets a similarity.
        """
        provider = self.hub.get(game.model)
        resolved, vec = provider.vector_for(norm, lemma)
        if vec is not None:
            target_vec = provider.vectors[provider.index[game.target]]
            sim = float(vec @ target_vec)
            rank = provider.rank_in_vocab(game.target, resolved)
            return resolved, sim, rank, False

        # Fallback: SimCSE can encode arbitrary input via the transformer.
        sc = self.hub.providers.get("simcse")
        if sc is None or game.target not in sc.index:
            return None, 0.0, None, False
        resolved_sc, vec_sc = sc.vector_for(norm, lemma)
        if vec_sc is None:
            return None, 0.0, None, False
        target_sc = sc.vectors[sc.index[game.target]]
        sim = float(vec_sc @ target_sc)
        return resolved_sc, sim, None, True

    def _guess_vectors(self, game: Game) -> tuple[np.ndarray, list[tuple[int, np.ndarray]]]:
        """Return target vector and list of ``(history_index, vec)`` for guesses
        that have a vector in the *active* model. Fallback guesses (scored via
        SimCSE while the game is on fastText) are skipped — they appear in the
        list view but not on the spatial visualizations."""
        provider = self.hub.get(game.model)
        target_vec = provider.vectors[provider.index[game.target]]
        indexed: list[tuple[int, np.ndarray]] = []
        for i, g in enumerate(game.guesses):
            if g.fallback:
                continue
            if g.word in provider.index:
                indexed.append((i, provider.vectors[provider.index[g.word]]))
        return target_vec, indexed

    def _snapshot(self, game: Game) -> dict:
        target_vec, indexed = self._guess_vectors(game)
        guess_vecs = [v for _, v in indexed]
        circles = circles_layout(target_vec, guess_vecs)
        history = [_guess_to_dict(g) for g in game.guesses]
        for h in history:
            h["circle"] = None
        for k, (i, _) in enumerate(indexed):
            if k < len(circles["guesses"]):
                history[i]["circle"] = circles["guesses"][k]
        return {
            "game_id": game.id,
            "model": game.model,
            "solved": game.solved,
            "n_guesses": len(game.guesses),
            "vocab_size": self.hub.vocab_size(game.model),
            "history": history,
            "circles": circles,
            "target": game.target if game.solved else None,
        }

    def get_sky(self, game: Game) -> dict:
        target_vec, indexed = self._guess_vectors(game)
        guess_vecs = [v for _, v in indexed]
        sky = starry_sky_layout(target_vec, guess_vecs)
        for k, (i, _) in enumerate(indexed):
            if k < len(sky["guesses"]):
                sky["guesses"][k]["word"] = game.guesses[i].word
                sky["guesses"][k]["rank"] = game.guesses[i].rank
        return sky


def _guess_to_dict(g: Guess) -> dict:
    return {
        "word": g.word,
        "raw": g.raw,
        "sim": g.sim,
        "rank": g.rank,
        "fallback": g.fallback,
    }
