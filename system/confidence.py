"""
confidence.py — Interaction Confidence Scoring
===============================================
Scores how reliably an interaction actually changed frontend state.
A low score triggers escalation rather than blind retry.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ConfidenceLevel(str, Enum):
    HIGH   = "HIGH"    # >= 0.85 — proceed
    MEDIUM = "MEDIUM"  # 0.60–0.84 — proceed with logged warning
    LOW    = "LOW"     # 0.35–0.59 — retry once then escalate
    FAILED = "FAILED"  # < 0.35 — stop, escalate to human


@dataclass
class ConfidenceSignal:
    name: str
    weight: float        # 0.0–1.0 contribution weight
    passed: bool
    detail: str = ""


@dataclass
class InteractionConfidence:
    """
    Aggregates signals into a single score and level.

    Signals (all weighted):
      - visual_state_changed     Did the visible DOM change after interaction?
      - value_persisted          Does the field still hold the value 500ms later?
      - no_rerender_wipe         Did a rerender revert the value?
      - selector_stable          Did the target element stay in the DOM?
      - hydration_ready          Was the element interactive before we touched it?
      - validation_passed        Does the page show no error on this field?
      - retry_penalty            Deduct per retry (first attempt is neutral)
    """

    action: str = ""
    target: str = ""
    signals: List[ConfidenceSignal] = field(default_factory=list)
    retry_count: int = 0
    raw_score: float = 0.0
    level: ConfidenceLevel = ConfidenceLevel.FAILED
    summary: str = ""

    # Weights must sum to 1.0
    _WEIGHTS = {
        "visual_state_changed": 0.30,
        "value_persisted":      0.25,
        "no_rerender_wipe":     0.20,
        "selector_stable":      0.10,
        "hydration_ready":      0.08,
        "validation_passed":    0.07,
    }
    _RETRY_PENALTY = 0.08  # per retry beyond the first

    def add_signal(self, name: str, passed: bool, detail: str = "") -> None:
        weight = self._WEIGHTS.get(name, 0.05)
        self.signals.append(ConfidenceSignal(name=name, weight=weight, passed=passed, detail=detail))

    def compute(self) -> "InteractionConfidence":
        """Calculate raw_score and level from accumulated signals."""
        if not self.signals:
            self.raw_score = 0.0
            self.level = ConfidenceLevel.FAILED
            self.summary = "No signals recorded."
            return self

        total_weight = sum(s.weight for s in self.signals)
        passed_weight = sum(s.weight for s in self.signals if s.passed)
        base = (passed_weight / total_weight) if total_weight > 0 else 0.0

        # Retry penalty: each retry beyond first deducts 0.08
        penalty = max(0, self.retry_count - 1) * self._RETRY_PENALTY
        self.raw_score = max(0.0, round(base - penalty, 3))

        if self.raw_score >= 0.85:
            self.level = ConfidenceLevel.HIGH
        elif self.raw_score >= 0.60:
            self.level = ConfidenceLevel.MEDIUM
        elif self.raw_score >= 0.35:
            self.level = ConfidenceLevel.LOW
        else:
            self.level = ConfidenceLevel.FAILED

        failed_signals = [s.name for s in self.signals if not s.passed]
        self.summary = (
            f"score={self.raw_score:.2f} level={self.level.value} "
            f"retries={self.retry_count} "
            f"failed_signals={failed_signals or 'none'}"
        )
        return self

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "target": self.target,
            "score": self.raw_score,
            "level": self.level.value,
            "retry_count": self.retry_count,
            "summary": self.summary,
            "signals": [
                {"name": s.name, "passed": s.passed, "weight": s.weight, "detail": s.detail}
                for s in self.signals
            ],
        }

    @property
    def should_escalate(self) -> bool:
        return self.level in (ConfidenceLevel.LOW, ConfidenceLevel.FAILED)

    @property
    def should_retry(self) -> bool:
        return self.level == ConfidenceLevel.LOW and self.retry_count < 2
