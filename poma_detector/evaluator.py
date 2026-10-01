"""
Stage 4: Model Evaluator & Benchmark Metrics

Computes academic security evaluation metrics (Precision, Recall, F1 Score, FP/FN rates)
comparing POMABuster outputs against ground-truth audit benchmark datasets.
"""

from typing import List, Set, Dict
from .models import POMAlert, DetectionReport


class ModelEvaluator:
    """Evaluates detection accuracy against benchmark ground truths."""

    @staticmethod
    def calculate_metrics(detected_poma_txs: List[str],
                          ground_truth_poma_txs: List[str],
                          total_transactions: int = 0,
                          total_trades: int = 0,
                          suspicious_count: int = 0) -> DetectionReport:
        """
        Computes Precision, Recall, and F1 Score.
        """
        detected_set = set(t.lower() for t in detected_poma_txs)
        truth_set = set(t.lower() for t in ground_truth_poma_txs)

        true_positives = len(detected_set.intersection(truth_set))
        false_positives = len(detected_set - truth_set)
        false_negatives = len(truth_set - detected_set)

        precision = (true_positives / (true_positives + false_positives)) if (true_positives + false_positives) > 0 else 0.0
        recall = (true_positives / (true_positives + false_negatives)) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        # Construct dummy alerts for reporting metadata if needed
        alerts = []

        return DetectionReport(
            total_transactions_analyzed=total_transactions,
            total_trades_recovered=total_trades,
            suspicious_trades_flagged=suspicious_count,
            alerts_generated=alerts,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1_score, 4)
        )
