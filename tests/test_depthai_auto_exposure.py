import pytest
import cv2
import depthai as dai
import numpy as np
from depthai_auto_exposure import AutoExposureRegion, clamp

# Create pipeline
pipeline = dai.Pipeline()
camRgb = pipeline.create(dai.node.ColorCamera)
camRgb.setPreviewSize((1920, 1080))
camRgb.setInterleaved(False)
xoutRgb = pipeline.create(dai.node.XLinkOut)
xoutRgb.setStreamName("rgb")
camRgb.preview.link(xoutRgb.input)

# Define fixture to run before each test
@pytest.fixture(autouse=True)
def run_around_tests():
    with dai.Device(pipeline) as device:
        qControl = device.getInputQueue(name="camControl")
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        region = AutoExposureRegion()
        step = region.step

        yield

        # Clean up after each test
        qControl.send(dai.CameraControl())
        cv2.destroyAllWindows()

# Test AutoExposureRegion class
class TestAutoExposureRegion:
    def test_grow(self):
        region = AutoExposureRegion()
        region.grow(10, 20)
        assert region.size == (210, 220)

    def test_move(self):
        region = AutoExposureRegion()
        region.move(30, 40)
        assert region.position == (30, 40)

    def test_endPosition(self):
        region = AutoExposureRegion()
        region.position = (50, 60)
        region.size = (100, 200)
        assert region.endPosition() == (150, 260)

    def test_toRoi(self):
        region = AutoExposureRegion()
        region.position = (100, 200)
        region.size = (300, 400)
        region.resolution = (640, 480)
        assert np.array_equal(region.toRoi(), np.array([100, 200, 300, 400]) * region.resolution[1] // 1080)

# Test clamp function
def test_clamp():
    assert clamp(5, 1, 10) == 5
    assert clamp(-5, 1, 10) == 1
    assert clamp(15, 1, 10) == 10

# Test auto-exposure control
def test_auto_exposure():
    with dai.Device(pipeline) as device:
        qControl = device.getInputQueue(name="camControl")
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        frame = None
        detections = []
        nnRegion = True
        region = AutoExposureRegion()
        def displayFrame(name, frame):
            if not nnRegion:
                cv2.rectangle(frame, region.position, region.endPosition(), (0, 255, 0), 2)
            cv2.imshow(name, frame)

        while True:
            inRgb = qRgb.tryGet()
            if inRgb is not None:
                frame = inRgb.getCvFrame()
            if frame is not None:
                displayFrame("rgb", frame)
            key = cv2.waitKey(1)
            if key == ord('n'):
                nnRegion = True
            elif key in [ord('w'), ord('a'), ord('s'), ord('d'), ord('+'), ord('-')]:
                nnRegion = False
                if key == ord('a'):
                    region.move(x=-region.step)
                if key == ord('d'):
                    region.move(x=region.step)
                if key == ord

