import pytest

def run_tests():
    # List of test files to run
    test_files = [
        "test_crop_cls_image.py",
        "test_f1_score.py",
        "test_recognition.py",
        "test_get_sign_text.py",
        "test_detection.py"
        ]

    # Run pytest for the specified test files
    pytest.main(test_files + ["-p", "no:warnings","-v","--html=report.html","--self-contained-html"])

if __name__ == "__main__":
    run_tests()
