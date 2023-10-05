import pytest
from model import f1_score
from tensorflow.keras.metrics import Recall, Precision

def test_f1_score_known_values():
    y_true = [1, 0, 1, 1, 0, 1]
    y_pred = [1, 0, 0, 1, 0, 1]
    
    precision_metric = Precision()
    recall_metric = Recall()
    
    precision_val = precision_metric(y_true, y_pred).numpy()
    recall_val = recall_metric(y_true, y_pred).numpy()
    expected_f1 = 2 * ((precision_val * recall_val) / (precision_val + recall_val + 1e-5))
    
    assert f1_score(y_true, y_pred) == pytest.approx(expected_f1)

def test_f1_score_all_zeros():
    y_true_zeros = [0, 0, 0, 0]
    y_pred_zeros = [0, 0, 0, 0]
    assert f1_score(y_true_zeros, y_pred_zeros) == pytest.approx(1.0, rel=1e-5)

def test_f1_score_all_ones():
    y_true_ones = [1, 1, 1, 1]
    y_pred_ones = [1, 1, 1, 1]
    assert f1_score(y_true_ones, y_pred_ones) == pytest.approx(1.0, rel=1e-5)
