"""Debate Hub - Structured debate coordination for multiple agents."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class DebatePhase(Enum):
    OPENING = "opening"
    ARGUMENT = "argument"
    REBUTTAL = "rebuttal"
    SYNTHESIS = "synthesis"
    VOTING = "voting"
    CONCLUSION = "conclusion"


class SynthesisMethod(Enum):
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"


class AgentType(Enum):
    NVIDIA_GPU = "nvidia"
    AWS_TRAINIUM = "trainium"
    GOOGLE_TPU = "tpu"
    CPU = "cpu"


class Protocol(Enum):
    MCP = "mcp"
    A2A = "a2a"
    CUSTOM = "custom"
    HTTP = "http"


@dataclass
class Agent:
    agent_id: str
    name: str
    agent_type: AgentType = AgentType.CPU
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"agent_id": self.agent_id, "name": self.name, "agent_type": self.agent_type.value}


@dataclass
class Perspective:
    perspective_id: str
    agent_id: str
    interpretation: str
    confidence: float = 0.0
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {"perspective_id": self.perspective_id, "agent_id": self.agent_id, 
                "interpretation": self.interpretation, "confidence": self.confidence}


@dataclass
class DebateRound:
    round_id: str
    phase: DebatePhase
    participant_ids: List[str]
    statements: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {"round_id": self.round_id, "phase": self.phase.value, 
                "statements": self.statements}


@dataclass
class ConsensusResult:
    success: bool
    synthesis: str = ""
    confidence: float = 0.0
    perspectives: List[Perspective] = field(default_factory=list)
    debate_rounds: List[DebateRound] = field(default_factory=list)
    agreement_level: float = 0.0
    dissenting_opinions: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class DebateConfig:
    max_rounds: int = 5
    min_participants: int = 2
    confidence_threshold: float = 0.7
    agreement_threshold: float = 0.8
    enable_rebuttal: bool = True


class ConsensusEngine:
    """Coordinates multiple agent perspectives with structured debate."""
    
    def __init__(self, config: Optional[DebateConfig] = None):
        self.config = config or DebateConfig()
        self._perspectives: Dict[str, List[Perspective]] = {}
    
    async def delegate_and_deliberate(
        self,
        question: str,
        agents: List[Agent],
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """Main entry point: delegate question to agents and deliberate."""
        if len(agents) < self.config.min_participants:
            return ConsensusResult(success=False, error=f"Need at least {self.config.min_participants} agents")
        
        perspectives = []
        for agent in agents:
            perspective = Perspective(
                perspective_id=str(uuid.uuid4()),
                agent_id=agent.agent_id,
                interpretation=f"Perspective from {agent.name}: {question}",
                confidence=0.75
            )
            perspectives.append(perspective)
        
        # Run debate rounds
        debate_rounds = []
        if self.config.enable_rebuttal and len(agents) > 1:
            debate_rounds = await self._run_debate(question, perspectives, agents)
        
        result = self._synthesize(perspectives, debate_rounds, agents)
        return result
    
    async def _run_debate(self, question: str, perspectives: List[Perspective], agents: List[Agent]) -> List[DebateRound]:
        debate_rounds = []
        participant_ids = [a.agent_id for a in agents]
        
        # Opening
        debate_rounds.append(DebateRound(
            round_id=str(uuid.uuid4()),
            phase=DebatePhase.OPENING,
            participant_ids=participant_ids,
            statements={p.agent_id: p.interpretation for p in perspectives}
        ))
        
        # Argument rounds
        for round_num in range(1, self.config.max_rounds):
            debate_rounds.append(DebateRound(
                round_id=str(uuid.uuid4()),
                phase=DebatePhase.ARGUMENT,
                participant_ids=participant_ids,
                statements={p.agent_id: f"Argument from {p.agent_id}" for p in perspectives}
            ))
            
            if self.config.enable_rebuttal:
                debate_rounds.append(DebateRound(
                    round_id=str(uuid.uuid4()),
                    phase=DebatePhase.REBUTTAL,
                    participant_ids=participant_ids,
                    statements={p.agent_id: f"Rebuttal from {p.agent_id}" for p in perspectives}
                ))
        
        # Synthesis
        debate_rounds.append(DebateRound(
            round_id=str(uuid.uuid4()),
            phase=DebatePhase.SYNTHESIS,
            participant_ids=participant_ids,
            statements={p.agent_id: f"Synthesis: {p.interpretation}" for p in perspectives}
        ))
        
        return debate_rounds
    
    def _synthesize(self, perspectives: List[Perspective], debate_rounds: List[DebateRound], agents: List[Agent]) -> ConsensusResult:
        if not perspectives:
            return ConsensusResult(success=False, error="No perspectives")
        
        # Calculate agreement
        confidences = [p.confidence for p in perspectives]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        variance = sum((c - avg_conf) ** 2 for c in confidences) / max(len(confidences), 1)
        agreement = 1.0 - min(variance ** 0.5, 1.0)
        
        # Synthesis
        best = max(perspectives, key=lambda p: p.confidence) if perspectives else None
        synthesis = f"Synthesized: {best.interpretation[:100]}" if best else ""
        
        return ConsensusResult(
            success=True,
            synthesis=synthesis,
            confidence=avg_conf,
            perspectives=perspectives,
            debate_rounds=debate_rounds,
            agreement_level=agreement
        )
    
    async def quick_consensus(self, question: str, agents: List[Agent]) -> ConsensusResult:
        """Quick consensus without full debate."""
        original = self.config.enable_rebuttal
        self.config.enable_rebuttal = False
        result = await self.delegate_and_deliberate(question, agents)
        self.config.enable_rebuttal = original
        return result


__all__ = ["ConsensusEngine", "Perspective", "DebateRound", "ConsensusResult", "DebateConfig", "Agent", "DebatePhase", "SynthesisMethod"]
