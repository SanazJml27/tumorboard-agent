"""
Data schemas shared across all agents.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationCategory(str, Enum):
    CONTINUE_CURRENT_THERAPY = "continue_current_therapy"
    TARGETED_THERAPY = "targeted_therapy"
    IMMUNOTHERAPY = "immunotherapy"
    CLINICAL_TRIAL = "clinical_trial"
    PALLIATIVE_SUPPORTIVE_CARE = "palliative_supportive_care"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class EscalationTier(str, Enum):
    AUTO_FINALIZE = "auto_finalize"
    SENIOR_REVIEW = "senior_review"
    URGENT_ESCALATION = "urgent_escalation"


class PatientFactors(BaseModel):
    performance_status: Optional[str] = None  # e.g. "ECOG 1"
    comorbidities: List[str] = Field(default_factory=list)
    patient_preferences: Optional[str] = None


class Case(BaseModel):
    case_id: str
    cancer_type: str
    stage: Optional[str] = None
    imaging_findings: str = ""
    pathology_findings: str = ""
    genomic_findings: List[str] = Field(default_factory=list)
    patient_factors: PatientFactors = Field(default_factory=PatientFactors)


class AgentOpinion(BaseModel):
    agent_name: str
    round_number: int
    recommendation: RecommendationCategory
    confidence: float
    rationale: str
    cited_evidence: List[str] = Field(default_factory=list)
    facts_considered: List[str] = Field(default_factory=list)


class CatfishChallenge(BaseModel):
    round_number: int
    rule_id: str
    target_consensus: RecommendationCategory
    challenge_text: str
    cited_evidence: List[str] = Field(default_factory=list)


class DebateRound(BaseModel):
    round_number: int
    opinions: List[AgentOpinion]
    majority_recommendation: RecommendationCategory
    agreement_score: float
    catfish_challenge: Optional[CatfishChallenge] = None


class ConsensusResult(BaseModel):
    final_recommendation: RecommendationCategory
    final_confidence: float
    final_agreement_score: float
    rounds_conducted: int
    dissenting_agents: List[str] = Field(default_factory=list)
    catfish_intervened: bool = False
    summary_text: str = ""


class OversightDecision(BaseModel):
    tier: EscalationTier
    reasons: List[str] = Field(default_factory=list)


class AgentTraceEvent(BaseModel):
    agent: str
    action: str
    detail: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TumorBoardReport(BaseModel):
    case_id: str
    consensus: ConsensusResult
    oversight: OversightDecision
    rounds: List[DebateRound]
    trace: List[AgentTraceEvent]
