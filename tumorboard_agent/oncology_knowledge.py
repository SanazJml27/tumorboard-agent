"""
Structured oncology "actionable findings" mapping.

This is deliberately separate from knowledge_base.json (which holds free-text
snippets used for RAG-style citation retrieval). This module holds the
*decisive* structured logic: a keyword -> (recommendation, confidence tier,
evidence tag, kb citation) mapping that specialist agents use to reach a
recommendation deterministically and auditably -- similar in spirit to a
(much simplified, original, non-clinical) actionable-mutation database.

Every entry here is written from general public scientific understanding of
biomarker-therapy class relationships, phrased originally, and is for
demonstration only -- it is not a substitute for a real curated clinical
knowledge base (e.g. OncoKB, NCCN, ESMO) and must never inform real
treatment decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from tumorboard_agent.schemas import RecommendationCategory


@dataclass(frozen=True)
class ActionableFinding:
    recommendation: RecommendationCategory
    confidence_tier: float  # 0-1, how strong/established the evidence is
    kb_id: str
    tag: str  # "actionable" | "trial_relevant" | "conflict_flag"


# Keyword -> finding. Keywords are matched case-insensitively as substrings
# against genomic_findings / pathology_findings text.
ACTIONABLE_FINDINGS: Dict[str, ActionableFinding] = {
    "egfr": ActionableFinding(RecommendationCategory.TARGETED_THERAPY, 0.9, "kb-egfr", "actionable"),
    "alk": ActionableFinding(RecommendationCategory.TARGETED_THERAPY, 0.9, "kb-alk", "actionable"),
    "her2": ActionableFinding(RecommendationCategory.TARGETED_THERAPY, 0.88, "kb-her2", "actionable"),
    "brca1": ActionableFinding(RecommendationCategory.TARGETED_THERAPY, 0.85, "kb-brca", "actionable"),
    "brca2": ActionableFinding(RecommendationCategory.TARGETED_THERAPY, 0.85, "kb-brca", "actionable"),
    "kras g12c": ActionableFinding(RecommendationCategory.CLINICAL_TRIAL, 0.55, "kb-krasg12c", "trial_relevant"),
    "msi-h": ActionableFinding(RecommendationCategory.IMMUNOTHERAPY, 0.85, "kb-msi", "actionable"),
    "dmmr": ActionableFinding(RecommendationCategory.IMMUNOTHERAPY, 0.85, "kb-msi", "actionable"),
    "pd-l1 high": ActionableFinding(RecommendationCategory.IMMUNOTHERAPY, 0.7, "kb-pdl1", "actionable"),
    "er+": ActionableFinding(RecommendationCategory.CONTINUE_CURRENT_THERAPY, 0.7, "kb-er-pr-hormone", "actionable"),
    "er positive": ActionableFinding(RecommendationCategory.CONTINUE_CURRENT_THERAPY, 0.7, "kb-er-pr-hormone", "actionable"),
    "triple negative": ActionableFinding(RecommendationCategory.IMMUNOTHERAPY, 0.5, "kb-triple-negative", "actionable"),
}

# Combinations that are biologically atypical enough to warrant confirmatory
# testing before committing to a recommendation.
CONFLICT_COMBINATIONS = [
    (("msi-h", "tmb-low"), "kb-tmb-low-conflict"),
    (("dmmr", "tmb-low"), "kb-tmb-low-conflict"),
]


def find_actionable(text: str) -> Optional[ActionableFinding]:
    """Return the strongest actionable finding mentioned in the text, if any."""

    lowered = text.lower()
    matches = [f for kw, f in ACTIONABLE_FINDINGS.items() if kw in lowered]
    if not matches:
        return None
    return max(matches, key=lambda f: f.confidence_tier)


def find_all_actionable(text: str) -> list[tuple[str, ActionableFinding]]:
    lowered = text.lower()
    return [(kw, f) for kw, f in ACTIONABLE_FINDINGS.items() if kw in lowered]


def find_conflict(text: str) -> Optional[str]:
    """Return a kb_id if the text contains a biologically conflicting combination."""

    lowered = text.lower()
    for keywords, kb_id in CONFLICT_COMBINATIONS:
        if all(kw in lowered for kw in keywords):
            return kb_id
    return None
