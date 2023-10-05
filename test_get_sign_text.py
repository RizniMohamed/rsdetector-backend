import pytest
from model import get_text

# Sample known labels and their expected texts for testing
# For this example, let's assume your CSV has entries for labels '5', '2', and '8' with texts 'Five', 'Two', and 'Eight' respectively.
KNOWN_LABELS = [
    ('0', 'Stop to give priority to vehicles on the adjacent road'),
    ('1', 'Pedestrian Crossing'),
    ('2', 'Pedestrian Crossing Ahead'),
    ('3', 'Speed Limit for heavy vehicles in non built-up areas'),
    ('4', 'Bus Stop'),
    ('5', 'Children present/ crossing Ahead'),
    ('6', 'No Parking'),
    ('7', 'Right Bend Ahead'),
    ('8', 'Traffic From Left Merges Ahead'),
    ('9', 'Traffic From Right Merges Ahead'),
    ('10', 'Light Signals Ahead'),
]

@pytest.mark.parametrize("label, expected_text", KNOWN_LABELS)
def test_get_text_known_labels(label, expected_text):
    assert get_text(label) == expected_text

def test_get_text_non_existent_label():
    non_existent_label = '999'  # Assuming '999' doesn't exist in your CSV
    with pytest.raises(Exception):  # Assuming get_text raises an exception for non-existent labels
        get_text(non_existent_label)
