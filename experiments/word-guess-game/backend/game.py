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
        provider = self.hub.get(game.model)
        resolved, vec = self.hub.vector_for(raw_word, model=game.model)
        if vec is None:
            return {
                "ok": False,
                "error": "unknown_word",
                "message": f'Slovo "{raw_word}" neznám. Zkus jiné.',
            }

        target_vec = provider.vectors[provider.index[game.target]]
        sim = float(vec @ target_vec)
        rank = provider.rank_in_vocab(game.target, resolved)

        if any(g.word == resolved for g in game.guesses):
            existing = next(g for g in game.guesses if g.word == resolved)
            return {
                "ok": True,
                "duplicate": True,
                "guess": _guess_to_dict(existing),
                **self._snapshot(game),
            }

        guess = Guess(word=resolved, raw=raw_word.strip(), sim=sim, rank=rank, ts=time.time())
        game.guesses.append(guess)

        if resolved == game.target:
            game.solved = True

        return {
            "ok": True,
            "duplicate": False,
            "guess": _guess_to_dict(guess),
            **self._snapshot(game),
        }

    def _guess_vectors(self, game: Game) -> tuple[np.ndarray, list[np.ndarray]]:
        provider = self.hub.get(game.model)
        target_vec = provider.vectors[provider.index[game.target]]
        guess_vecs: list[np.ndarray] = []
        for g in game.guesses:
            if g.word in provider.index:
                guess_vecs.append(provider.vectors[provider.index[g.word]])
            else:
                # Should not normally happen — submit_guess already resolved a vector.
                # Re-resolve to keep snapshot complete.
                _, v = self.hub.vector_for(g.word, model=game.model)
                if v is not None:
                    guess_vecs.append(v)
        return target_vec, guess_vecs

    def _snapshot(self, game: Game) -> dict:
        target_vec, guess_vecs = self._guess_vectors(game)
        circles = circles_layout(target_vec, guess_vecs)
        history = [_guess_to_dict(g) for g in game.guesses]
        for i, h in enumerate(history):
            h["circle"] = circles["guesses"][i] if i < len(circles["guesses"]) else None
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
        target_vec, guess_vecs = self._guess_vectors(game)
        sky = starry_sky_layout(target_vec, guess_vecs)
        for i, g in enumerate(game.guesses):
            if i < len(sky["guesses"]):
                sky["guesses"][i]["word"] = g.word
                sky["guesses"][i]["rank"] = g.rank
        return sky


def _guess_to_dict(g: Guess) -> dict:
    return {
        "word": g.word,
        "raw": g.raw,
        "sim": g.sim,
        "rank": g.rank,
    }
