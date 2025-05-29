"""
Information Collection Subgraph

Manages conversations with users to collect missing resume information.
Updated to directly accept InterruptData from resume_tailorer.py
"""

from .graph import info_collection_graph
from .state import (
    InfoCollectionState,
    create_info_collection_state_from_interrupt,
    create_info_collection_state,
)

__all__ = [
    "info_collection_graph",
    "InfoCollectionState",
    "create_info_collection_state_from_interrupt",
    "create_info_collection_state",
]
