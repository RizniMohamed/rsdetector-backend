import pytest
import numpy as np
from model import crop_cls_image

def create_dummy_image():
    return np.linspace(0, 255, 640*640).reshape(640, 640).astype(np.uint8)

def test_crop_cls_image_known_values():
    dummy_image = create_dummy_image()
    x1, y1, x2, y2 = 100, 100, 250, 250
    cropped_image = crop_cls_image(x1, y1, x2, y2, dummy_image)
    assert cropped_image.shape == (150, 150)

def test_crop_cls_image_edge_case_at_edge():
    dummy_image = create_dummy_image()
    x1, y1, x2, y2 = 0, 0, 150, 150
    cropped_image = crop_cls_image(x1, y1, x2, y2, dummy_image)
    assert cropped_image.shape == (150, 150)

def test_crop_cls_image_edge_case_small_bbox():
    dummy_image = create_dummy_image()
    x1, y1, x2, y2 = 300, 300, 310, 310
    cropped_image = crop_cls_image(x1, y1, x2, y2, dummy_image)
    assert cropped_image.shape == (150, 150)

def test_crop_cls_image_edge_case_large_bbox():
    dummy_image = create_dummy_image()
    x1, y1, x2, y2 = 0, 0, 640, 640
    cropped_image = crop_cls_image(x1, y1, x2, y2, dummy_image)
    assert cropped_image.shape == (150, 150)
