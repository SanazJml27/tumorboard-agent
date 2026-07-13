"""
Genomics / Molecular Tumor Board Agent.

The most specialized agent: reasons purely over genomic_findings against
the structured actionable-finding mapping. This is the agent most likely
to surface a trial-relevant-but-uncited mutation, which is exactly the
scenario the catfish agent's "trial_eligible_mutation_uncited" rule looks
for in the other agents' rationale/citations.
"""

from __future__ import annotations

from tumorboard_agent.agents.base_specialist import BaseSpecialistAgent
from tumorboard_agent.oncology_knowledge import find_actionable, find_all_actionable
from tumorboard_agent.schemas import AgentOpinion, Case, RecommendationCategory


class GenomicsAgent(BaseSpecialistAgent):
    name = "GenomicsAgent"

    def initial_opinion(self, case: Case) -> AgentOpinion:
        text = " ".join(case.genomic_findings)
        lowered = text.lower()
        facts = []
        citations = []

        all_matches = find_all_actionable(text)
        finding = find_actionable(text)

        negative_markers = ["no pathogenic", "no actionable", "wild-type", "wild type", "negative for"]

        if finding:
            recommendation = finding.recommendation
            confidence = finding.confidence_tier
            facts.append(f"Molecular profile includes: {', '.join(case.genomic_findings) or 'n/a'}")
            citations.append(finding.kb_id)
            if len(all_matches) > 1:
                facts.append(
                    "Multiple actionable findings present; prioritizing the one with strongest evidence tier."
                )
        elif case.genomic_findings and any(m in lowered for m in negative_markers):
            recommendation = RecommendationCategory.CONTINUE_CURRENT_THERAPY
            confidence = 0.65
            facts.append(f"Panel testing explicitly reported as negative for actionable findings: '{text}'.")
        elif case.genomic_findings:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.3
            facts.append(f"Genomic findings reported ({', '.join(case.genomic_findings)}) but none map to a recognized actionable category.")
        else:
            recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            confidence = 0.2
            facts.append("No genomic/molecular testing results available for this case.")

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
