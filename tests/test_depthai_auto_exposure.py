import pytest
import subprocess
import time
import cv2
import depthai as dai
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from depthai_auto_exposure import AutoExposureRegion

def test_camera():
    cap = cv2.VideoCapture(0)
    assert cap.isOpened() == True
    cap.release()

def test_depthai():
    with pytest.raises(RuntimeError, match="No available devices"):
        from depthai_auto_exposure import pipeline
        with dai.Device(pipeline) as device:
            pass
