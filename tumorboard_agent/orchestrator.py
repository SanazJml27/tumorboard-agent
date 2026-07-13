"""
Orchestrator.

Runs the full tumor board debate:

  Round 1: each specialist gives an independent opinion.
  Moderator scores agreement.
  Catfish reviews the round -- if agreement is high AND a genuine
    counter-signal exists, it raises a structured challenge.
  Round 2 (only if challenged): specialists revise in light of the
    challenge; Moderator re-scores.
  Moderator finalizes consensus; Oversight assigns an escalation tier.

Every step is logged to a trace for explainability.
"""

from __future__ import annotations

from typing import List

from tumorboard_agent.agents.catfish_agent import CatfishAgent
from tumorboard_agent.agents.genomics_agent import GenomicsAgent
from tumorboard_agent.agents.moderator_agent import ModeratorAgent
from tumorboard_agent.agents.navigator_agent import NurseNavigatorAgent
from tumorboard_agent.agents.oncologist_agent import MedicalOncologistAgent
from tumorboard_agent.agents.oversight_agent import OversightAgent
from tumorboard_agent.agents.pathologist_agent import PathologistAgent
from tumorboard_agent.agents.radiologist_agent import RadiologistAgent
from tumorboard_agent.knowledge_base import KnowledgeBase
from tumorboard_agent.llm_provider import LLMProvider, get_llm_provider
from tumorboard_agent.schemas import AgentTraceEvent, Case, DebateRound, TumorBoardReport

MAX_ROUNDS = 3


class TumorBoardOrchestrator:
    def __init__(self, llm: LLMProvider | None = None):
        kb = KnowledgeBase()
        llm = llm or get_llm_provider()
        self.specialists = [
            MedicalOncologistAgent(kb, llm),
            RadiologistAgent(kb, llm),
            PathologistAgent(kb, llm),
            GenomicsAgent(kb, llm),
            NurseNavigatorAgent(kb, llm),
        ]
        self.moderator = ModeratorAgent(llm)
        self.catfish = CatfishAgent()
        self.oversight = OversightAgent()

    def run(self, case: Case) -> TumorBoardReport:
        trace: List[AgentTraceEvent] = []
        rounds: List[DebateRound] = []
        catfish_intervened = False

        # --- Round 1: independent opinions ---
        opinions = [s.initial_opinion(case) for s in self.specialists]
        for o in opinions:
            trace.append(
                AgentTraceEvent(
                    agent=o.agent_name,
                    action="initial_opinion",
                    detail=f"{o.recommendation.value} (confidence={o.confidence})",
                )
            )

        current_round = self.moderator.score_round(1, opinions)
        trace.append(
            AgentTraceEvent(
                agent=self.moderator.name,
                action="score_round",
                detail=f"round=1 majority={current_round.majority_recommendation.value} "
                f"agreement={current_round.agreement_score}",
            )
        )
        rounds.append(current_round)

        round_number = 1
        while round_number < MAX_ROUNDS:
            challenge = self.catfish.review(
                case,
                round_number,
                current_round.opinions,
                current_round.agreement_score,
                current_round.majority_recommendation,
            )
            if challenge is None:
                trace.append(
                    AgentTraceEvent(
                        agent=self.catfish.name,
                        action="review",
                        detail=f"round={round_number}: no genuine counter-signal found; no challenge raised.",
                    )
                )
                break

            catfish_intervened = True
            current_round.catfish_challenge = challenge
            trace.append(
                AgentTraceEvent(
                    agent=self.catfish.name,
                    action="challenge",
                    detail=f"round={round_number}: [{challenge.rule_id}] {challenge.challenge_text}",
                )
            )

            round_number += 1
            revised_opinions = []
            for specialist, prior in zip(self.specialists, current_round.opinions):
                revised = specialist.maybe_revise(case, prior, challenge)
                revised_opinions.append(revised)
                trace.append(
                    AgentTraceEvent(
                        agent=specialist.name,
                        action="revise_opinion",
                        detail=f"{prior.recommendation.value}(conf={prior.confidence}) -> "
                        f"{revised.recommendation.value}(conf={revised.confidence})",
                    )
                )

            current_round = self.moderator.score_round(round_number, revised_opinions)
            trace.append(
                AgentTraceEvent(
                    agent=self.moderator.name,
                    action="score_round",
                    detail=f"round={round_number} majority={current_round.majority_recommendation.value} "
                    f"agreement={current_round.agreement_score}",
                )
            )
            rounds.append(current_round)

        consensus = self.moderator.finalize(case, rounds, catfish_intervened)
        trace.append(
            AgentTraceEvent(
                agent=self.moderator.name,
                action="finalize",
                detail=f"final={consensus.final_recommendation.value} "
                f"confidence={consensus.final_confidence} rounds={consensus.rounds_conducted}",
            )
        )

        oversight_decision = self.oversight.decide(consensus)
        trace.append(
            AgentTraceEvent(
                agent=self.oversight.name,
                action="decide_tier",
                detail=f"tier={oversight_decision.tier.value} reasons={oversight_decision.reasons}",
            )
        )

        return TumorBoardReport(
            case_id=case.case_id,
            consensus=consensus,
            oversight=oversight_decision,
            rounds=rounds,
            trace=trace,
        )
