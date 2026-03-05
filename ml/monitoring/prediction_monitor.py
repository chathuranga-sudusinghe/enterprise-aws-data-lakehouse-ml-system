# ml/monitoring/prediction_monitor.py

from collections import defaultdict


class PredictionMonitor:
    """
    Tracks prediction distribution and risk tier counts.
    """

    def __init__(self):
        self.total_predictions = 0
        self.tier_counts = defaultdict(int)

    def record_prediction(self, probability: float):
        """
        Record prediction probability and assign risk tier.
        """

        self.total_predictions += 1

        if probability >= 0.8:
            tier = "high_risk"
        elif probability >= 0.5:
            tier = "medium_risk"
        else:
            tier = "low_risk"

        self.tier_counts[tier] += 1

    def summary(self):
        """
        Return monitoring summary.
        """

        return {
            "total_predictions": self.total_predictions,
            "tier_distribution": dict(self.tier_counts),
        }