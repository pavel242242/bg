# Přihořívá hoří 🔥

Česká slovní hra ve stylu [Contexto](https://contexto.me) / [Semantle](https://semantle.com).
Hráč hádá tajné slovo, hra mu po každém tipu ukazuje, jak je sémanticky blízko.
Tři vizualizace ukazují herní stav z různých úhlů.

## Co je pod kapotou

- **Embeddingy:** [fastText `cc.cs.300`](https://fasttext.cc/docs/en/crawl-vectors.html) (předpočítané, 2 M českých slov) + alternativně [`Seznam/simcse-small-e-czech`](https://huggingface.co/Seznam/simcse-small-e-czech) (sentence-transformer pro porovnání).
- **Lemmatizace + POS tagging:** [LINDAT UDPipe REST API](https://lindat.mff.cuni.cz/services/udpipe) (model `czech-pdtc-ud-2.17`). Cache na disku.
- **Slovník cílových slov:** ~2 500 podstatných jmen z [hermitdave/FrequencyWords cs_50k](https://github.com/hermitdave/FrequencyWords) (OpenSubtitles), filtrovaných UDPipe POS tagy + simplemma slovníkem.
- **2D projekce:** PCA (soustředné kruhy, sklearn) + UMAP (hvězdná obloha, umap-learn). Souhvězdí = MST nad cosine vzdáleností.
- **Backend:** FastAPI + uvicorn.
- **Frontend:** vanilla HTML/CSS/JS + D3.js (CDN).

## Rychlý start

Předpoklady: Python 3.11, [uv](https://docs.astral.sh/uv/) (`curl -Ls https://astral.sh/uv/install.sh | sh`).

Pokud máš datové soubory v `data/` (vocab.json, embeddings*.npz, …), stačí:

```bash
uv sync
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8765
```

Pak otevři <http://127.0.0.1:8765>.

## Postavení od nuly

Pokud potřebuješ data vyrobit (cca 5 min + ~1.2 GB stažení):

```bash
uv sync

# 1. frekvenční seznam (1.5 MB)
curl -sSL -o data/cs_50k_raw.txt \
  https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/cs/cs_50k.txt

# 2. POS tagging + lemmatizace přes UDPipe (~3 min, cache se uloží)
uv run python scripts/build_vocab.py

# 3. fastText vektory (1.2 GB stažení; po extrakci se mohou smazat)
curl -sSL -o data/cc.cs.300.vec.gz \
  https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.cs.300.vec.gz
uv run python scripts/extract_embeddings.py
rm data/cc.cs.300.vec.gz

# 4. (volitelně) SimCSE embeddingy pro porovnání modelů
uv run python scripts/precompute_simcse.py

# 5. Pročistit cílový seznam slov
uv run python scripts/clean_targets.py
```

## API

| Endpoint | Metoda | Popis |
|---|---|---|
| `/api/health` | GET | Stav, dostupné modely, počty slov |
| `/api/new-game` | POST `{ seed?, model? }` | Nová hra (`model = "fasttext" \| "simcse"`) |
| `/api/guess` | POST `{ game_id, word }` | Tip; vrací rank, sim, kruhové layouty |
| `/api/sky/{game_id}` | GET | UMAP layout + MST hran (souhvězdí) |
| `/api/reveal` | POST `{ game_id }` | Odkrýt tajné slovo |

## Architektura vizualizací

### 1. Seznam (Contexto styl)
Tipy tříděné dle ranku v 10 386-slovním slovníku podstatných jmen. Heat-color barvy: top 50 = červená, top 250 = oranžová, top 1000 = žlutá, dál chladně modré.

### 2. Soustředné kruhy
Radiální vzdálenost = `1 - cosine_similarity` k tajnému slovu (přesné, ne aproximace).
Úhel = projekce přes 2D PCA na (target + tipy).
Kruhy adaptivně rozdělují prostor na kvartily aktuálního maxima.

### 3. Hvězdná obloha
Volný 2D layout přes UMAP nad cosine metrikou.
Souhvězdí = minimum spanning tree přes cosine vzdálenosti v původním embeddingovém prostoru (ne přes 2D pozice — zachovává sémantickou strukturu).

## Volba embeddingu — proč fastText jako default

Pro single-word podobnost bez kontextu (klasický Contexto/Semantle case) je statický word embedding (word2vec/fastText) přesně to, na co je trénovaný. Výhody oproti transformerům:

- Žádná inference za běhu — lookup je sub-milisekunda.
- Subword n-gramy zvládnou OOV tipy (překlepy, neologismy).
- 91 % pokrytí naší 50k frekvenční slovní zásoby.

SimCSE je k dispozici jako srovnání — sentence-transformer modely mají kompresnější similarity rozsah (~0.85–0.95 vs 0.05–0.95 u fastTextu) a chytí jiné typy souvislostí (kontextové, syntaktické). Pro hru často působí překvapivě.

## Co by se dalo přidat

- [ ] Týdenní seed-of-the-day pro shared challenge
- [ ] Definice tajného slova po vyhrání (Wiktionary API)
- [ ] Hint systém ("nejbližší tip je rank 50, odpověď leží v top 10")
- [ ] Persistovat hry do SQLite pro share/historii
- [ ] OpenAI / Cohere embedding jako třetí model (vyžaduje API klíč)
- [ ] Ensemble fastText + SimCSE (re-ranking top-N)
