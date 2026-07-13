"""
Base class for specialist agents.

Each specialist implements `initial_opinion()` with its own deterministic
domain logic, and inherits a shared `maybe_revise()` that reacts to a
catfish challenge in a bounded, auditable way -- confidence adjustments and
category changes are table-driven, not left to free generation.
"""

from __future__ import annotations

from typing import List, Optional

from tumorboard_agent.knowledge_base import KnowledgeBase
from tumorboard_agent.llm_provider import LLMProvider
from tumorboard_agent.schemas import AgentOpinion, Case, CatfishChallenge, RecommendationCategory

# How much a challenge that is squarely in an agent's domain lowers its
# confidence, vs. one that's only tangentially relevant.
DIRECT_HIT_PENALTY = 0.25
INDIRECT_HIT_PENALTY = 0.1

# Which rule_ids are squarely in which agent's domain (gets the bigger
# penalty and is eligible to change its recommendation category).
DOMAIN_RULES = {
    "performance_status_conflict": {"MedicalOncologist", "GenomicsAgent", "NurseNavigator"},
    "trial_eligible_mutation_uncited": {"MedicalOncologist", "Pathologist", "GenomicsAgent"},
    "conflicting_biomarkers": {"Pathologist", "GenomicsAgent"},
    "patient_preference_conflict": {"MedicalOncologist", "NurseNavigator"},
}


class BaseSpecialistAgent:
    name = "BaseSpecialistAgent"

    def __init__(self, kb: KnowledgeBase, llm: LLMProvider):
        self._kb = kb
        self._llm = llm

    def initial_opinion(self, case: Case) -> AgentOpinion:
        raise NotImplementedError

    def maybe_revise(
        self, case: Case, prior: AgentOpinion, challenge: CatfishChallenge
    ) -> AgentOpinion:
        """Default revision logic: lower confidence; downgrade to a safer
        category if confidence drops far enough and the challenge is
        squarely in this agent's domain. Subclasses may override for
        more specific behavior.
        """

        directly_challenged = self.name in DOMAIN_RULES.get(challenge.rule_id, set())
        penalty = DIRECT_HIT_PENALTY if directly_challenged else INDIRECT_HIT_PENALTY
        new_confidence = max(0.05, round(prior.confidence - penalty, 3))

        new_recommendation = prior.recommendation
        new_facts = list(prior.facts_considered) + [
            f"Revised after catfish challenge ({challenge.rule_id}): {challenge.challenge_text}"
        ]
        new_citations = list(dict.fromkeys(prior.cited_evidence + challenge.cited_evidence))

        if directly_challenged and new_confidence < 0.5:
            if challenge.rule_id == "trial_eligible_mutation_uncited":
                new_recommendation = RecommendationCategory.CLINICAL_TRIAL
            elif challenge.rule_id == "performance_status_conflict":
                new_recommendation = RecommendationCategory.PALLIATIVE_SUPPORTIVE_CARE
            elif challenge.rule_id == "conflicting_biomarkers":
                new_recommendation = RecommendationCategory.INSUFFICIENT_EVIDENCE
            elif challenge.rule_id == "patient_preference_conflict":
                new_recommendation = RecommendationCategory.PALLIATIVE_SUPPORTIVE_CARE

        rationale = self._compose_rationale(
            case,
            new_recommendation,
            new_facts,
            [self._kb.get(cid) for cid in new_citations if self._kb.get(cid)],
            revision_note=challenge.challenge_text,
        )

        return AgentOpinion(
            agent_name=self.name,
            round_number=prior.round_number + 1,
            recommendation=new_recommendation,
            confidence=new_confidence,
            rationale=rationale,
            cited_evidence=new_citations,
            facts_considered=new_facts,
        )

    def _compose_rationale(
        self,
        case: Case,
        recommendation: RecommendationCategory,
        facts: List[str],
        citations: List[Optional[dict]],
        revision_note: Optional[str] = None,
    ) -> str:
        citation_texts = [f"[{c['kb_id']}] {c['text']}" for c in citations if c]
        lines = [
            f"{self.name} recommends: {recommendation.value.replace('_', ' ')}.",
            "Facts considered: " + ("; ".join(facts) if facts else "none specific to this case."),
        ]
        if citation_texts:
            lines.append("Supporting background: " + " | ".join(citation_texts))
        if revision_note:
            lines.append(f"Revised opinion in light of: {revision_note}")

        prompt = "\n".join(lines)
        return self._llm.complete(
            system_prompt=(
                f"You are the {self.name} on a virtual tumor board. Phrase the "
                "given facts and recommendation clearly and concisely for a "
                "clinical audience. Do not add any new facts, numbers, or "
                "claims beyond what is given."
            ),
            user_prompt=prompt,
        )
