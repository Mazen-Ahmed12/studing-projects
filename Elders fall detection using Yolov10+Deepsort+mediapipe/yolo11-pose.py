import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

model = YOLO("/content/yolo11s.pt")

cap = cv2.VideoCapture("/content/Elders-fall.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Use 'avc1' codec for mp4 (works better in Colab)
out = cv2.VideoWriter(
    "/content/output.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps if fps > 0 else 25,
    (width, height),
)

tracker = DeepSort(
    max_age=10,
    nn_budget=100,
    embedder="clip_RN50",
    embedder_gpu=True,
    max_iou_distance=0.7,
    n_init=3,
)
frame_count = 0
max_frames = 200

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.7)
    detections = []

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0].item())
            if cls == 0:  # person class
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                w, h = x2 - x1, y2 - y1
                detections.append(((x1, y1, w, h), conf, cls))

    tracks = tracker.update_tracks(detections, frame=frame)

    for track in tracks:
        if not track.is_confirmed():
            continue

        track_id = track.track_id
        ltrb = track.to_ltrb()
        x1, y1, x2, y2 = map(int, ltrb)

        height = y2 - y1
        width = x2 - x1

        if height - width < 0:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                frame,
                "SOMEONE FELL",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
            )

        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                str(track_id),
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

    out.write(frame)

out.release()
cap.release()
cv2.destroyAllWindows()
