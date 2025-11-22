import cv2
from ultralytics import YOLO
import os
from vidgear.gears import CamGear
import requests

# This temporarily sets the environment variable KMP_DUPLICATE_LIB_OK to TRUE for your current command session, which suppresses the Error #15 and allows the program to run past that conflict.
model = YOLO(
    "D:/mazen/EagleVision/projects/studing-projects/flask/YOLO-integeration-with-flask/model/yolov11s.pt"
)


def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True, classes=[0])

        for result in results:
            for box in result.boxes:
                boxes = box.xyxy.cpu().numpy()
                track_ids = box.id.cpu().numpy() if box.id is not None else []

                for box, track_id in zip(boxes, track_ids):
                    x1, y1, x2, y2 = box
                    height = y2 - y1
                    width = x2 - x1

                    if height - width < 0:
                        fall_message = (
                            f"FALL DETECTED: Track ID {track_id} in Frame {frame_id}."
                        )
                        detection_data = {
                            "track_id": track_id,
                            "frame_id": frame_id,
                            "fall_message": fall_message,
                        }
                        detections.append(detection_data)

        frame_id += 1

    cap.release()
    return detections


def process_url(video_url):
    """Processes a video URL (including YouTube) using Vidgear for streaming."""
    stream = CamGear(source=video_url, stream_mode=True, logging=True).start()

    frame_id = 0
    detections = []

    while True:
        frame = stream.read()
        if frame is None:
            break

        results = model.track(frame, persist=True, classes=[0])

        for result in results:
            for box in result.boxes:
                boxes = box.xyxy.cpu().numpy()
                track_ids = box.id.cpu().numpy() if box.id is not None else []

                for box, track_id in zip(boxes, track_ids):
                    x1, y1, x2, y2 = box
                    height = y2 - y1
                    width = x2 - x1

                    if height - width < 0:
                        fall_message = (
                            f"FALL DETECTED: Track ID {track_id} in Frame {frame_id}."
                        )
                        detection_data = {
                            "track_id": track_id,
                            "frame_id": frame_id,
                            "fall_message": fall_message,
                        }
                        detections.append(detection_data)

        frame_id += 1

    stream.stop()
    return detections


def process_live(cam_index=0):
    cap = cv2.VideoCapture(cam_index)
    frame_id = 0
    detections = []

    while True:
        _, frame = cap.read()
        if not _:
            break

        results = model.track(frame, persist=True, classes=[0])
        for r in results:
            for box in r.boxes:
                box = box.xyxy.cpu().numpy()
                track_ids = box.id.cpu().numpy() if box.id is not None else []

                for box, track_id in zip(boxes, track_ids):
                    x1, y1, x2, y2 = box
                    height = y2 - y1
                    width = x2 - x1

                    if height - width < 0:
                        fall_message = (
                            f"FALL DETECTED: Track ID {track_id} in Frame {frame_id}."
                        )
                        detection_data = {
                            "track_id": track_id,
                            "frame_id": frame_id,
                            "fall_message": fall_message,
                        }
                        detections.append(detection_data)
        frame_id += 1
    cap.release()
    return detections
