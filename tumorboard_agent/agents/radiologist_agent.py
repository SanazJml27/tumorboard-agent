"""
Radiologist Agent.

Reads structured imaging findings text (no actual image processing in this
demo -- see README for why) and reasons about disease trajectory.
"""

from __future__ import annotations

from tumorboard_agent.agents.base_specialist import BaseSpecialistAgent
from tumorboard_agent.schemas import AgentOpinion, Case, RecommendationCategory

AMBIGUOUS_TERMS = ["indeterminate", "equivocal", "cannot be excluded"]


class RadiologistAgent(BaseSpecialistAgent):
    name = "Radiologist"

    def initial_opinion(self, case: Case) -> AgentOpinion:
        text = case.imaging_findings.lower()
        facts = []
        citations = []
        confidence_penalty = 0.15 if any(t in text for t in AMBIGUOUS_TERMS) else 0.0

        if "stable" in text or "partial response" in text or "no new lesion" in text:
            recommendation = RecommendationCategory.CONTINUE_CURRENT_THERAPY
            confidence = 0.75 - confidence_penalty
            facts.append("Imaging shows stable disease or partial response.")
            citations.append("kb-imaging-stable")
        elif "new lesion" in text or "progression" in text or "metastasis" in text:
            recommendation = RecommendationCategory.CLINICAL_TRIAL
            confidence = 0.6 - confidence_penalty
            facts.append("Imaging shows progression/new lesion(s), suggesting re-evaluation of current therapy.")
            citations.append("kb-imaging-progression")
        else:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.3
            facts.append("Imaging findings do not clearly indicate progression or stability.")

        if confidence_penalty:
            facts.append("Report language includes ambiguous/equivocal phrasing, lowering confidence.")

        rationale = self._compose_rationale(
            case, recommendation, facts, [self._kb.get(c) for c in citations]
        )
        return AgentOpinion(
            agent_name=self.name,
            round_number=1,
            recommendation=recommendation,
            confidence=max(0.1, round(confidence, 3)),
            rationale=rationale,
            cited_evidence=citations,
            facts_considered=facts,
        )
