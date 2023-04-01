import pytest
import subprocess
import time
import cv2
import numpy as np
import depthai as dai
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from depthai_auto_exposure import AutoExposureRegion

@pytest.mark.timeout(30)
def test_auto_exposure():
    process = subprocess.Popen(['python', 'auto_exposure.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # wait for the script to start up and show the video feed
    assert process.poll() is None  # assert that the process is still running
    process.terminate()  # terminate the process

def test_manual_roi_movement():
    pipeline = dai.Pipeline()
    camRgb = pipeline.create(dai.node.ColorCamera)
    camRgb.setPreviewSize((1920, 1080))
    camRgb.setInterleaved(False)
    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")
    camRgb.preview.link(xoutRgb.input)
    with dai.Device(pipeline) as device:
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        frame = None
        region = AutoExposureRegion()
        region.move(x=50, y=50)  # move the ROI to the top left corner
        for i in range(10):
            inRgb = qRgb.tryGet()
            if inRgb is not None:
                frame = inRgb.getCvFrame()
            if frame is not None:
                cv2.rectangle(frame, region.position, region.endPosition(), (0, 255, 0), 2)
                cv2.imshow("rgb", frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()
        assert region.position == (50, 50)  # assert that the ROI moved to the correct position

