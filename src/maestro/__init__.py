"""Maestro OS - Multi-Agent Orchestration System

Components:
- Detector: Dynamic agent scaling based on project complexity
- Orchestrator: End-to-end workflow coordination
- ConsensusEngine: Super-majority voting (3/5)
- QueueExecutor: Worker pool with rate limiting
- ML Pipeline: Routing, duration prediction, risk classification
"""

__version__ = "6.0.0"
__author__ = "Manta Associados"

from .orchestrator import MaestroOrchestrator
from .detector import ComplexityDetector
from .consensus import ConsensusEngine
from .queue_executor import QueueExecutor
from .parser import WorkflowParser

__all__ = [
    "MaestroOrchestrator",
    "ComplexityDetector",
    "ConsensusEngine",
    "QueueExecutor",
    "WorkflowParser",
]
