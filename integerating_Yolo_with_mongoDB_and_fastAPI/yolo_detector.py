import cv2
from ultralytics import YOLO

# This temporarily sets the environment variable KMP_DUPLICATE_LIB_OK to TRUE for your current command session, which suppresses the Error #15 and allows the program to run past that conflict.
model = YOLO(
    "D:\mazen\EagleVision\projects\studing-projects\integerating_Yolo_with_Postgresql_and_fastAPI\yolov11s.pt"
)


def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise HTTPException(status_code=400, detail="Could not open video file")

    frame_id = 0
    detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True, classes=[0], device="cuda")

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
                            "track_id": float(track_id),
                            "frame_id": float(frame_id),
                            "fall_message": str(fall_message),
                        }
                        detections.append(detection_data)

        frame_id += 1

    cap.release()
    return detections
