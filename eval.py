#!/usr/bin/env python3
"""
Evaluation harness for TumorBoard-Agent.

Runs the pipeline against the synthetic case set and compares the output
to data/eval_gold.json, which records expected system behavior (a
regression/calibration check the developer verified, not external clinical
ground truth -- see README). Reports recommendation accuracy, tier
accuracy, and catfish-trigger calibration.

Usage:
    python eval.py
"""

from __future__ import annotations

import json
from pathlib import Path

from tumorboard_agent.orchestrator import TumorBoardOrchestrator
from tumorboard_agent.schemas import Case

DATA_DIR = Path(__file__).resolve().parent / "data"


def main() -> None:
    with open(DATA_DIR / "synthetic_cases.json", "r", encoding="utf-8") as f:
        cases = {c["case_id"]: c for c in json.load(f)}
    with open(DATA_DIR / "eval_gold.json", "r", encoding="utf-8") as f:
        gold = json.load(f)

    orchestrator = TumorBoardOrchestrator()

    rec_correct = 0
    tier_correct = 0
    catfish_correct = 0
    rows = []

    for g in gold:
        case = Case(**cases[g["case_id"]])
        report = orchestrator.run(case)

        rec_ok = report.consensus.final_recommendation.value == g["expected_recommendation"]
        tier_ok = report.oversight.tier.value == g["expected_tier"]
        catfish_ok = report.consensus.catfish_intervened == g["expected_catfish"]

        rec_correct += rec_ok
        tier_correct += tier_ok
        catfish_correct += catfish_ok

        rows.append(
            (
                g["case_id"],
                report.consensus.final_recommendation.value,
                g["expected_recommendation"],
                rec_ok,
                report.oversight.tier.value,
                g["expected_tier"],
                tier_ok,
                report.consensus.catfish_intervened,
                g["expected_catfish"],
                catfish_ok,
            )
        )

    n = len(gold)
    print(f"{'case':<10} {'recommendation (got/expected)':<45} {'tier (got/expected)':<35} {'catfish (got/exp)'}")
    print("-" * 120)
    for (cid, rec, exp_rec, rec_ok, tier, exp_tier, tier_ok, cf, exp_cf, cf_ok) in rows:
        mark = lambda ok: "OK " if ok else "FAIL"
        print(
            f"{cid:<10} {mark(rec_ok)} {rec:<20}/{exp_rec:<20} "
            f"{mark(tier_ok)} {tier:<16}/{exp_tier:<16} "
            f"{mark(cf_ok)} {str(cf):<5}/{str(exp_cf)}"
        )

    print("-" * 120)
    print(f"Recommendation accuracy: {rec_correct}/{n} ({rec_correct/n:.0%})")
    print(f"Tier accuracy:           {tier_correct}/{n} ({tier_correct/n:.0%})")
    print(f"Catfish calibration:     {catfish_correct}/{n} ({catfish_correct/n:.0%})")


if __name__ == "__main__":
    main()
