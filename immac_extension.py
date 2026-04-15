"""IMMAC-inspired communication utilities.

This module adds an intrinsic-motivation communication layer that can be
plugged into multi-agent systems.
"""

from dataclasses import dataclass
from math import exp
from typing import Dict, List, Tuple


@dataclass
class AgentMessage:
    """Message payload shared by an agent."""

    sender_id: int
    observation: Dict[str, str]
    intrinsic_value: float


class IntrinsicScorer:
    """Estimate surprise from feature frequencies."""

    def __init__(self):
        self.feature_counts: Dict[Tuple[str, str], int] = {}
        self.total_events = 0

    def score(self, observation: Dict[str, str]) -> float:
        """Higher score means observation is rarer/more surprising."""
        if not observation:
            return 0.0

        self.total_events += 1
        scores = []

        for feature, value in observation.items():
            key = (feature, str(value))
            count = self.feature_counts.get(key, 0)
            self.feature_counts[key] = count + 1

            # Rare values produce larger surprise scores.
            rarity = 1.0 / (count + 1)
            scores.append(rarity)

        return sum(scores) / len(scores)


class CommunicationGate:
    """Send only important messages using intrinsic thresholding."""

    def __init__(self, threshold: float = 0.35):
        self.threshold = threshold

    def should_send(self, intrinsic_value: float) -> bool:
        return intrinsic_value >= self.threshold


class AttentionRouter:
    """Weight incoming messages by intrinsic value and select top-k."""

    @staticmethod
    def _softmax(values: List[float]) -> List[float]:
        if not values:
            return []

        max_v = max(values)
        exps = [exp(v - max_v) for v in values]
        denom = sum(exps)
        return [v / denom for v in exps]

    def prioritize(self, messages: List[AgentMessage], top_k: int = 2) -> List[Tuple[AgentMessage, float]]:
        if not messages:
            return []

        weights = self._softmax([m.intrinsic_value for m in messages])
        ranked = sorted(zip(messages, weights), key=lambda x: x[1], reverse=True)
        return ranked[: max(1, top_k)]


def build_intrinsic_messages(
    observations: List[Dict[str, str]],
    scorer: IntrinsicScorer,
    gate: CommunicationGate,
) -> List[AgentMessage]:
    """Convert observations into gated messages."""
    messages: List[AgentMessage] = []

    for idx, obs in enumerate(observations):
        intrinsic_value = scorer.score(obs)
        if gate.should_send(intrinsic_value):
            messages.append(
                AgentMessage(
                    sender_id=idx,
                    observation=obs,
                    intrinsic_value=intrinsic_value,
                )
            )

    return messages
