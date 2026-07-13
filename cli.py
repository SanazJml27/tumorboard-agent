#!/usr/bin/env python3
"""
Command-line entry point for TumorBoard-Agent.

Usage:
    python cli.py --demo                    # run all synthetic demo cases
    python cli.py --demo-id case-002        # run a single demo case
    python cli.py --demo-id case-002 --trace
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tumorboard_agent.orchestrator import TumorBoardOrchestrator
from tumorboard_agent.schemas import Case, TumorBoardReport

DEMO_PATH = Path(__file__).resolve().parent / "data" / "synthetic_cases.json"


def print_report(report: TumorBoardReport, show_trace: bool) -> None:
    print("=" * 76)
    print(f"Case: {report.case_id}")
    for r in report.rounds:
        print("-" * 76)
        print(f"Round {r.round_number} -- majority: {r.majority_recommendation.value} "
              f"(agreement {r.agreement_score:.0%})")
        for o in r.opinions:
            print(f"  [{o.agent_name:<18}] {o.recommendation.value:<28} conf={o.confidence}")
        if r.catfish_challenge:
            c = r.catfish_challenge
            print(f"  >> CATFISH [{c.rule_id}]: {c.challenge_text}")

    print("-" * 76)
    print(f"FINAL RECOMMENDATION: {report.consensus.final_recommendation.value}")
    print(f"Confidence: {report.consensus.final_confidence:.0%} | "
          f"Agreement: {report.consensus.final_agreement_score:.0%} | "
          f"Rounds: {report.consensus.rounds_conducted} | "
          f"Catfish intervened: {report.consensus.catfish_intervened}")
    if report.consensus.dissenting_agents:
        print(f"Dissenting: {', '.join(report.consensus.dissenting_agents)}")
    print(f"Summary: {report.consensus.summary_text}")
    print("-" * 76)
    print(f"OVERSIGHT TIER: {report.oversight.tier.value.upper()}")
    for reason in report.oversight.reasons:
        print(f"  - {reason}")

    if show_trace:
        print("-" * 76)
        print("Full agent trace:")
        for event in report.trace:
            print(f"  [{event.timestamp}] {event.agent} :: {event.action} -> {event.detail}")
    print("=" * 76)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TumorBoard-Agent pipeline.")
    parser.add_argument("--demo", action="store_true", help="Run all synthetic demo cases.")
    parser.add_argument("--demo-id", type=str, help="Run a single synthetic demo case by ID.")
    parser.add_argument("--trace", action="store_true", help="Print the full agent trace.")
    args = parser.parse_args()

    orchestrator = TumorBoardOrchestrator()

    with open(DEMO_PATH, "r", encoding="utf-8") as f:
        all_cases = json.load(f)

    if args.demo_id:
        matches = [c for c in all_cases if c["case_id"] == args.demo_id]
        if not matches:
            raise SystemExit(f"No demo case with id {args.demo_id}")
        all_cases = matches
    elif not args.demo:
        parser.print_help()
        return

    for c in all_cases:
        case = Case(**c)
        report = orchestrator.run(case)
        print_report(report, args.trace)


if __name__ == "__main__":
    main()
