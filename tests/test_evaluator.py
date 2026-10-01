"""
Unit tests for Model Evaluator.
"""

import pytest
from poma_detector.evaluator import ModelEvaluator


def test_evaluator_metrics():
    detected = ["tx1", "tx2", "tx3", "tx4"]
    ground_truth = ["tx1", "tx2", "tx3", "tx5"]

    report = ModelEvaluator.calculate_metrics(detected, ground_truth)

    # TP = 3 (tx1, tx2, tx3), FP = 1 (tx4), FN = 1 (tx5)
    # Precision = 3 / (3+1) = 0.75
    # Recall = 3 / (3+1) = 0.75
    # F1 = 0.75

    assert report.precision == 0.75
    assert report.recall == 0.75
    assert report.f1_score == 0.75
