"""FastAPI app for the Czech word guessing game."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .embeddings import EmbeddingHub
from .game import GameManager

app = FastAPI(title="Přihořívá hoří", default_response_class=ORJSONResponse)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

hub = EmbeddingHub()
manager = GameManager(hub)


@app.on_event("startup")
def _warmup() -> None:
    # Pre-load the SimCSE model so the first OOV guess doesn't pay the load cost.
    sc = hub.providers.get("simcse")
    if sc is not None and hasattr(sc, "_ensure_model"):
        sc._ensure_model()


class NewGameBody(BaseModel):
    seed: str | None = None
    model: str = "fasttext"


class GuessBody(BaseModel):
    game_id: str
    word: str = Field(min_length=1, max_length=40)


class RevealBody(BaseModel):
    game_id: str


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "models": hub.available_models(),
        "vocab_sizes": {m: hub.vocab_size(m) for m in hub.available_models()},
        "n_targets": len(hub.targets),
        "n_active_games": len(manager.games),
    }


@app.post("/api/new-game")
def new_game(body: NewGameBody) -> dict:
    g = manager.new_game(seed=body.seed, model=body.model)
    return {
        "game_id": g.id,
        "model": g.model,
        "vocab_size": hub.vocab_size(g.model),
        "n_targets": len(hub.targets),
        "available_models": hub.available_models(),
    }


@app.post("/api/guess")
def guess(body: GuessBody) -> dict:
    g = manager.get(body.game_id)
    if g is None:
        raise HTTPException(status_code=404, detail="game_not_found")
    return manager.submit_guess(g, body.word)


@app.get("/api/sky/{game_id}")
def sky(game_id: str) -> dict:
    g = manager.get(game_id)
    if g is None:
        raise HTTPException(status_code=404, detail="game_not_found")
    return manager.get_sky(g)


@app.post("/api/reveal")
def reveal(body: RevealBody) -> dict:
    g = manager.get(body.game_id)
    if g is None:
        raise HTTPException(status_code=404, detail="game_not_found")
    g.solved = True
    return {"target": g.target}


# ---- frontend static serving ----

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")
