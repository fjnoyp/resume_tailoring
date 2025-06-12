"""
Cover Letter Processing Nodes

Processing nodes for cover letter generation and evaluation:
- cover_letter_generator: Generates cover letter based on tailored resume and feedback
- cover_letter_evaluator: Evaluates the generated cover letter with scoring

Uses the same patterns as resume_rewrite nodes for consistency.
"""

from .cover_letter_node import cover_letter_generator

__all__ = ["cover_letter_generator"] 