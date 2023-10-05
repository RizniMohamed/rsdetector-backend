import pytest
import cv2
from model import final_model_detection

def detection(frame):
    """Detect and recognize objects in the frame."""
    resized_frame = cv2.resize(frame, (640, 640))
    results = final_model_detection(resized_frame, conf=0.5)

    label_texts = []
    for r in results:
        if r:
            for b in r.boxes:
                label_texts.append(True)
    return len(label_texts)

def test_detection_with_sample_frame():
    frame = cv2.imread("./test_detection_images/single.PNG")
    assert detection(frame) == 1

def test_detection_with_no_objects():
    frame = cv2.imread("./test_detection_images/none.png")
    assert detection(frame) == 0

def test_detection_with_multiple_objects():
    frame = cv2.imread("./test_detection_images/multi.png")
    assert detection(frame) > 1
