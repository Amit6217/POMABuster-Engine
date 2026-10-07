"""
POMABuster Framework — Decentralized Finance (DeFi) Price Oracle Manipulation Attack Detector

An academic research implementation for detecting multi-transaction Price Oracle Manipulation Attacks (POMAs)
in EVM smart contracts based on SEC market manipulation rules.
"""

__version__ = "1.0.0"
__author__ = "Student Security Research"

from .models import Log, Trade, ArbitrageEvent, POMAlert, DetectionReport
from .semantics import SemanticRecoveryEngine
from .filtering import SECFilteringGate
from .linking import MultiTxLinkingEngine
from .evaluator import ModelEvaluator

__all__ = [
    "Log",
    "Trade",
    "ArbitrageEvent",
    "POMAlert",
    "DetectionReport",
    "SemanticRecoveryEngine",
    "SECFilteringGate",
    "MultiTxLinkingEngine",
    "ModelEvaluator",
]
