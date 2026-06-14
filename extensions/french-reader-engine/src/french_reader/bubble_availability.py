from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BubbleDetectorStatus:
    opencv_available: bool
    yolo_available: bool
    ready: bool
    detail: str


def _opencv_available() -> tuple[bool, str]:
    try:
        import cv2  # noqa: F401

        return True, f"opencv {cv2.__version__}"
    except ImportError:
        return False, "not installed — uv sync --extra bubble"


def _yolo_available() -> tuple[bool, str]:
    try:
        import ultralytics  # noqa: F401

        return True, f"ultralytics {ultralytics.__version__}"
    except ImportError:
        return False, "not installed — uv sync --extra bubble-yolo"


def get_bubble_detector_status() -> BubbleDetectorStatus:
    opencv_ok, opencv_detail = _opencv_available()
    yolo_ok, yolo_detail = _yolo_available()
    parts = [f"opencv={opencv_detail}", f"yolo={yolo_detail}"]
    return BubbleDetectorStatus(
        opencv_available=opencv_ok,
        yolo_available=yolo_ok,
        ready=opencv_ok or yolo_ok,
        detail="; ".join(parts),
    )
