import numpy as np
from ml.utils.threshold import find_optimal_threshold

def test_threshold_function():

    y_true = np.array([0,1,0,1])
    y_prob = np.array([0.1,0.9,0.2,0.8])

    threshold = find_optimal_threshold(y_true, y_prob)

    assert 0 <= threshold <= 1