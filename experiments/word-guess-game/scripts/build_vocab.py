"""Build Czech vocabulary for the guessing game.

Pipeline:
1. Read frequency list (data/cs_50k_raw.txt — word + count per line).
2. Pre-filter: alphabetic Czech tokens, length 3-20, drop function words.
3. Tag + lemmatize via LINDAT UDPipe REST API (batched). Cache the raw output.
4. Aggregate by lemma. A lemma is included only if:
     - dominant POS is NOUN
     - NOUN frequency share >= 0.7
     - PROPN frequency share < 0.3
5. Targets: stricter (NOUN >= 0.85, PROPN < 0.1, has >= 2 inflectional forms).
6. Write data/vocab.json and data/target_words.json.
"""

from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "cs_50k_raw.txt"
CACHE = ROOT / "data" / "udpipe_cache.json"
VOCAB_OUT = ROOT / "data" / "vocab.json"
TARGETS_OUT = ROOT / "data" / "target_words.json"

UDPIPE_URL = "https://lindat.mff.cuni.cz/services/udpipe/api/process"
UDPIPE_MODEL = "czech"

STOPWORDS = {
    "a", "i", "ale", "nebo", "že", "se", "si", "je", "jsem", "jsi", "jsme",
    "jste", "jsou", "byl", "byla", "bylo", "byly", "byli", "být", "bych",
    "bychom", "byste", "by", "bys", "to", "ten", "ta", "ty", "toho", "té",
    "tě", "ti", "mu", "mi", "mě", "já", "on", "ona", "ono", "my",
    "vy", "oni", "ony", "ona", "můj", "tvůj", "jeho", "její", "náš", "váš",
    "jejich", "co", "kdo", "jak", "kde", "kdy", "proč", "tak", "už", "ještě",
    "pak", "tady", "tu", "tam", "sem", "tudy", "potom", "vlastně", "totiž",
    "asi", "snad", "možná", "určitě", "jistě", "samozřejmě",
    "ne", "ano", "jo", "no", "hej", "ach", "och", "hmm",
    "v", "ve", "z", "ze", "s", "k", "ke", "do", "od", "po", "pro",
    "při", "na", "o", "u", "za", "před", "pod", "nad", "mezi", "skrze",
    "bez", "přes", "kolem", "okolo", "podél", "vedle", "místo",
    "když", "až", "než", "dokud", "pokud", "jestli", "zda", "aby", "protože",
    "neboť", "tedy", "takže", "tudíž", "proto",
    "ho", "ji", "jí", "jim", "ně", "ní", "něj",
    "kterého", "která", "které", "který", "kterou", "kterými", "kterým",
    "tenhle", "tahle", "tohle", "tihle", "tyhle",
    "moc", "hodně", "málo", "trochu", "víc", "více", "méně", "nejvíc",
    "dobře", "špatně", "rychle", "pomalu", "lehce", "těžce",
    "kam", "odkud", "odtud",
}

WORD_RE = re.compile(r"^[a-záčďéěíňóřšťúůýž]{3,20}$")


def load_raw() -> dict[str, int]:
    out: dict[str, int] = {}
    with RAW.open() as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            word, freq = parts[0].lower(), int(parts[1])
            if word in STOPWORDS:
                continue
            if not WORD_RE.match(word):
                continue
            out[word] = freq
    return out


def udpipe_tag(words: list[str], client: httpx.Client) -> list[tuple[str, str, str]]:
    text = " ".join(words)
    resp = client.post(
        UDPIPE_URL,
        data={"tokenizer": "", "tagger": "", "model": UDPIPE_MODEL, "data": text},
        timeout=120,
    )
    resp.raise_for_status()
    conllu = resp.json()["result"]
    triples = []
    for line in conllu.splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 5:
            continue
        if "-" in cols[0] or "." in cols[0]:
            continue
        triples.append((cols[1], cols[2], cols[3]))
    return triples


def tag_all(words: list[str]) -> dict[str, tuple[str, str]]:
    """Return form -> (lemma, upos), with on-disk caching."""
    if CACHE.exists():
        cached = json.loads(CACHE.read_text())
        print(f"Loaded {len(cached)} cached UDPipe results", flush=True)
    else:
        cached = {}

    todo = [w for w in words if w not in cached]
    if not todo:
        return cached

    BATCH = 1000
    with httpx.Client() as client:
        for i in range(0, len(todo), BATCH):
            chunk = todo[i : i + BATCH]
            for attempt in range(4):
                try:
                    triples = udpipe_tag(chunk, client)
                    break
                except Exception as e:
                    wait = 2 ** attempt
                    print(f"  retry after {wait}s: {e}", flush=True)
                    time.sleep(wait)
            else:
                continue
            for form, lemma, upos in triples:
                cached[form] = (lemma, upos)
            print(f"  batch {i//BATCH + 1}/{(len(todo)+BATCH-1)//BATCH} done", flush=True)
    CACHE.write_text(json.dumps(cached, ensure_ascii=False))
    return cached


def main() -> int:
    word_freq = load_raw()
    print(f"Pre-filter: {len(word_freq)} candidate forms", flush=True)
    forms = list(word_freq.keys())
    tags = tag_all(forms)

    # Per-lemma POS distribution.
    lemma_pos: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    lemma_forms: dict[str, set[str]] = defaultdict(set)
    for form, freq in word_freq.items():
        if form not in tags:
            continue
        lemma, upos = tags[form]
        if not WORD_RE.match(lemma):
            continue
        lemma_pos[lemma][upos] += freq
        lemma_forms[lemma].add(form)

    # Build vocab.
    vocab: list[dict] = []
    for lemma, dist in lemma_pos.items():
        total = sum(dist.values())
        noun = dist.get("NOUN", 0)
        propn = dist.get("PROPN", 0)
        if total == 0:
            continue
        noun_ratio = noun / total
        propn_ratio = propn / total
        top_pos = max(dist.items(), key=lambda x: x[1])[0]
        if top_pos != "NOUN":
            continue
        if noun_ratio < 0.7 or propn_ratio >= 0.3:
            continue
        vocab.append({
            "lemma": lemma,
            "freq": noun,
            "n_forms": len(lemma_forms[lemma]),
            "noun_ratio": round(noun_ratio, 3),
            "propn_ratio": round(propn_ratio, 3),
        })
    vocab.sort(key=lambda x: -x["freq"])
    VOCAB_OUT.write_text(json.dumps(vocab, ensure_ascii=False, indent=0))
    print(f"Wrote {VOCAB_OUT} with {len(vocab)} noun lemmas", flush=True)

    # Targets: stricter & mid-frequency band so they're game-friendly.
    targets = [
        v["lemma"]
        for v in vocab
        if v["noun_ratio"] >= 0.85
        and v["propn_ratio"] < 0.1
        and v["n_forms"] >= 2
    ]
    targets = targets[80:3000]  # skip very generic top words
    TARGETS_OUT.write_text(json.dumps(targets, ensure_ascii=False, indent=0))
    print(f"Wrote {TARGETS_OUT} with {len(targets)} target candidates", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
