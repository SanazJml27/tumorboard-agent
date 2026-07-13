"""
Medical Oncologist Agent.

Focuses on systemic therapy candidacy: looks first at genomic/molecular
findings for an actionable route (the strongest evidence tier), falling
back to imaging trend if no actionable mutation is present.
"""

from __future__ import annotations

from tumorboard_agent.agents.base_specialist import BaseSpecialistAgent
from tumorboard_agent.oncology_knowledge import find_actionable
from tumorboard_agent.schemas import AgentOpinion, Case, RecommendationCategory


class MedicalOncologistAgent(BaseSpecialistAgent):
    name = "MedicalOncologist"

    def initial_opinion(self, case: Case) -> AgentOpinion:
        genomic_text = " ".join(case.genomic_findings)
        finding = find_actionable(genomic_text) or find_actionable(case.pathology_findings)

        facts = []
        citations = []

        if finding:
            recommendation = finding.recommendation
            confidence = finding.confidence_tier
            facts.append(f"Actionable finding detected: '{genomic_text or case.pathology_findings}'")
            citations.append(finding.kb_id)
        elif "stable" in case.imaging_findings.lower() or "partial response" in case.imaging_findings.lower():
            recommendation = RecommendationCategory.CONTINUE_CURRENT_THERAPY
            confidence = 0.7
            facts.append("No actionable molecular finding; imaging shows stable disease/response.")
            citations.append("kb-imaging-stable")
        elif "progression" in case.imaging_findings.lower() or "new lesion" in case.imaging_findings.lower():
            recommendation = RecommendationCategory.CLINICAL_TRIAL
            confidence = 0.45
            facts.append("No actionable molecular finding; imaging shows progression, standard options limited.")
            citations.append("kb-imaging-progression")
        else:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.3
            facts.append("No actionable molecular finding and imaging trend unclear.")

        rationale = self._compose_rationale(
            case, recommendation, facts, [self._kb.get(c) for c in citations]
        )
        return AgentOpinion(
            agent_name=self.name,
            round_number=1,
            recommendation=recommendation,
            confidence=confidence,
            rationale=rationale,
            cited_evidence=citations,
            facts_considered=facts,
        )
