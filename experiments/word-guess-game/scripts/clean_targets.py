"""Tighten the target word list using simplemma's Czech dictionary.

Filters out English subtitle contamination (river, baby, please, ...) and obvious
proper nouns. Conservative — keeps only lemmas that simplemma recognizes as Czech.
"""

import json
from pathlib import Path

import simplemma

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Words simplemma flags as known but are clearly English subtitle imports or
# colloquial / proper-name oddities we don't want as targets.
EXTRA_BAN = {
    "john", "baby", "frank", "charlie", "okay", "please", "fuck", "sorry",
    "hi", "hey", "miss", "mister", "sir", "madam",
    "logan", "phoebe", "gatsby", "ahn",
    "bro", "guy", "dude",
}


def main() -> None:
    targets = json.loads((DATA / "target_words.json").read_text())
    vocab = {r["lemma"]: r for r in json.loads((DATA / "vocab.json").read_text())}

    cleaned = []
    dropped = []
    for w in targets:
        if w in EXTRA_BAN:
            dropped.append(w)
            continue
        if not simplemma.is_known(w, lang="cs"):
            dropped.append(w)
            continue
        # Require at least 3 chars.
        if len(w) < 3:
            dropped.append(w)
            continue
        cleaned.append(w)

    (DATA / "target_words.json").write_text(json.dumps(cleaned, ensure_ascii=False))
    print(f"Targets: {len(targets)} -> {len(cleaned)} (dropped {len(dropped)})")
    print("Sample dropped:", dropped[:30])
    print("Sample kept:", cleaned[:20], "...", cleaned[-20:])


if __name__ == "__main__":
    main()
