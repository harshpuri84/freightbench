"""Command line entry point.

    python -m freightbench generate --n 200 --out corpus.jsonl
    python -m freightbench score --corpus corpus.jsonl --predictions preds.json
    python -m freightbench baseline --corpus corpus.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .generate import Generator
from .pathologies import PATHOLOGIES
from .naive import predictions as naive_predictions
from .score import Report, render, score_corpus


def _load_corpus(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def cmd_generate(args: argparse.Namespace) -> int:
    docs = Generator(seed=args.seed).corpus(args.n)
    out = Path(args.out)
    with out.open("w", encoding="utf-8") as fh:
        for d in docs:
            fh.write(json.dumps(d.to_json(), ensure_ascii=False) + "\n")
    print(f"wrote {len(docs)} documents to {out}")
    print(f"seed {args.seed} — regenerating with the same seed gives the same corpus")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    corpus = _load_corpus(Path(args.corpus))
    with Path(args.predictions).open(encoding="utf-8") as fh:
        preds = json.load(fh)
    report = score_corpus(corpus, preds)
    print(render(report))
    return 0


def cmd_baseline(args: argparse.Namespace) -> int:
    """Score the empty extractor: predicts nothing for every field.

    This exists to make one number legible. An extractor that returns nothing
    still scores well above zero, because abstaining on a genuinely absent field
    is correct behaviour. If a model cannot beat this, it is not extracting, it
    is guessing.
    """
    corpus = _load_corpus(Path(args.corpus))
    preds = {d["doc_id"]: [{} for _ in d["ground_truth"]["shipments"]] for d in corpus}
    report = score_corpus(corpus, preds)
    print(render(report))
    return 0


def cmd_naive(args: argparse.Namespace) -> int:
    """Score the bundled naive rule-based extractor, broken out by pathology."""
    corpus = _load_corpus(Path(args.corpus))
    preds = naive_predictions(corpus)
    print(render(score_corpus(corpus, preds)))

    print("\n\npass rate by pathology")
    print("-" * 60)
    by_path: dict[str, list[dict]] = {}
    for d in corpus:
        by_path.setdefault(d["pathology"], []).append(d)
    rows = []
    for key, docs in by_path.items():
        r = score_corpus(docs, {d["doc_id"]: preds[d["doc_id"]] for d in docs})
        rows.append((key, r.pass_rate("critical"), len(docs)))
    for key, rate, n in sorted(rows, key=lambda t: t[1]):
        print(f"  {key:<22} {rate:>6.1%} critical-field pass  (n={n})")
    return 0


def cmd_pathologies(_: argparse.Namespace) -> int:
    for p in PATHOLOGIES:
        print(f"\n{p.key}\n  {p.label}")
        print(f"  tests:   {p.what_it_tests}")
        print(f"  correct: {p.correct_behaviour}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="freightbench")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="write a synthetic corpus")
    g.add_argument("--n", type=int, default=200)
    g.add_argument("--seed", type=int, default=20260811)
    g.add_argument("--out", default="corpus.jsonl")
    g.set_defaults(func=cmd_generate)

    s = sub.add_parser("score", help="score predictions against a corpus")
    s.add_argument("--corpus", required=True)
    s.add_argument("--predictions", required=True)
    s.set_defaults(func=cmd_score)

    b = sub.add_parser("baseline", help="score the empty extractor")
    b.add_argument("--corpus", required=True)
    b.set_defaults(func=cmd_baseline)

    nv = sub.add_parser("naive", help="score the bundled naive extractor")
    nv.add_argument("--corpus", required=True)
    nv.set_defaults(func=cmd_naive)

    p = sub.add_parser("pathologies", help="describe what each pathology tests")
    p.set_defaults(func=cmd_pathologies)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
