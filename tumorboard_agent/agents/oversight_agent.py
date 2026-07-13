"""
Oversight Agent.

Implements a tiered-escalation pattern (modeled on "Tiered Agentic
Oversight", 2026): not every consensus is treated equally -- confident,
low-disagreement, unchallenged conclusions can auto-finalize, while
anything uncertain, contested, or flagged gets routed to a human review
tier instead of being silently accepted.
"""

from __future__ import annotations

from tumorboard_agent.schemas import ConsensusResult, EscalationTier, OversightDecision, RecommendationCategory

SENIOR_REVIEW_CONFIDENCE_THRESHOLD = 0.65
URGENT_AGREEMENT_THRESHOLD = 0.6


class OversightAgent:
    name = "Oversight"

    def decide(self, consensus: ConsensusResult) -> OversightDecision:
        reasons = []

        if (
            consensus.final_agreement_score < URGENT_AGREEMENT_THRESHOLD
            or consensus.final_recommendation == RecommendationCategory.INSUFFICIENT_EVIDENCE
        ):
            reasons.append(
                f"Low final agreement ({consensus.final_agreement_score:.0%}) or insufficient-evidence "
                "conclusion -- requires senior human review before any action."
            )
            return OversightDecision(tier=EscalationTier.URGENT_ESCALATION, reasons=reasons)

        if (
            consensus.final_confidence < SENIOR_REVIEW_CONFIDENCE_THRESHOLD
            or consensus.catfish_intervened
            or consensus.dissenting_agents
        ):
            if consensus.catfish_intervened:
                reasons.append("A catfish challenge was raised during discussion.")
            if consensus.dissenting_agents:
                reasons.append(f"Dissenting agent(s): {', '.join(consensus.dissenting_agents)}.")
            if consensus.final_confidence < SENIOR_REVIEW_CONFIDENCE_THRESHOLD:
                reasons.append(f"Final confidence ({consensus.final_confidence:.0%}) below auto-finalize threshold.")
            return OversightDecision(tier=EscalationTier.SENIOR_REVIEW, reasons=reasons)

        reasons.append("High agreement, high confidence, no catfish challenge, no dissent.")
        return OversightDecision(tier=EscalationTier.AUTO_FINALIZE, reasons=reasons)
