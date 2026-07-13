"""
Moderator (Chair) Agent.

Aggregates a round of specialist opinions into a majority recommendation
and an agreement score, and -- once debate concludes -- writes the final
consensus summary. Like the specialists, aggregation math is deterministic;
the LLM provider is only used to phrase the final narrative.
"""

from __future__ import annotations

from collections import Counter
from typing import List

from tumorboard_agent.llm_provider import LLMProvider
from tumorboard_agent.schemas import (
    AgentOpinion,
    Case,
    ConsensusResult,
    DebateRound,
)


class ModeratorAgent:
    name = "Moderator"

    def __init__(self, llm: LLMProvider):
        self._llm = llm

    def score_round(self, round_number: int, opinions: List[AgentOpinion]) -> DebateRound:
        counts = Counter(o.recommendation for o in opinions)
        majority_rec, majority_count = counts.most_common(1)[0]
        agreement_score = round(majority_count / len(opinions), 3)

        return DebateRound(
            round_number=round_number,
            opinions=opinions,
            majority_recommendation=majority_rec,
            agreement_score=agreement_score,
        )

    def finalize(self, case: Case, rounds: List[DebateRound], catfish_intervened: bool) -> ConsensusResult:
        final_round = rounds[-1]
        final_rec = final_round.majority_recommendation
        agreeing = [o for o in final_round.opinions if o.recommendation == final_rec]
        dissenting = [o.agent_name for o in final_round.opinions if o.recommendation != final_rec]
        final_confidence = round(sum(o.confidence for o in agreeing) / len(agreeing), 3) if agreeing else 0.0

        lines = [
            f"Tumor board consensus for case {case.case_id} ({case.cancer_type}):",
            f"Final recommendation: {final_rec.value.replace('_', ' ')}",
            f"Reached after {len(rounds)} round(s) of discussion, "
            f"final agreement {final_round.agreement_score:.0%}.",
        ]
        if dissenting:
            lines.append(f"Dissenting: {', '.join(dissenting)}.")
        if catfish_intervened:
            lines.append(
                "A catfish challenge was raised during discussion; the panel "
                "considered it before reaching this final position."
            )

        summary = self._llm.complete(
            system_prompt=(
                "You are the moderator of a virtual tumor board. Summarize "
                "the panel's conclusion clearly and neutrally, using only "
                "the facts given. Do not add new clinical claims."
            ),
            user_prompt="\n".join(lines),
        )

        return ConsensusResult(
            final_recommendation=final_rec,
            final_confidence=final_confidence,
            final_agreement_score=final_round.agreement_score,
            rounds_conducted=len(rounds),
            dissenting_agents=dissenting,
            catfish_intervened=catfish_intervened,
            summary_text=summary,
        )
