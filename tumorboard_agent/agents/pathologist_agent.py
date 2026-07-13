"""
Pathologist Agent.

Reasons over histology/biomarker text. Flags insufficient evidence when a
critical marker appears to be missing rather than guessing.
"""

from __future__ import annotations

from tumorboard_agent.agents.base_specialist import BaseSpecialistAgent
from tumorboard_agent.oncology_knowledge import find_actionable, find_conflict
from tumorboard_agent.schemas import AgentOpinion, Case, RecommendationCategory


class PathologistAgent(BaseSpecialistAgent):
    name = "Pathologist"

    def initial_opinion(self, case: Case) -> AgentOpinion:
        text = case.pathology_findings
        facts = []
        citations = []

        conflict_kb = find_conflict(text)
        finding = find_actionable(text)

        if conflict_kb:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.35
            facts.append("Biomarker combination in the report is atypical/conflicting; confirmatory testing advised.")
            citations.append(conflict_kb)
        elif finding:
            recommendation = finding.recommendation
            confidence = finding.confidence_tier
            facts.append(f"Pathology report indicates a recognized biomarker pattern: '{text}'")
            citations.append(finding.kb_id)
        elif "grade" in text.lower() or "margin" in text.lower():
            recommendation = RecommendationCategory.CONTINUE_CURRENT_THERAPY
            confidence = 0.6
            facts.append("Histologic detail present but no clearly actionable biomarker reported.")
        else:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.25
            facts.append("Pathology report appears to be missing key biomarker detail.")

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
