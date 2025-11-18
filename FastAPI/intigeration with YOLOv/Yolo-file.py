import cv2
from ultralytics import YOLO
import cvzone

model = YOLO(
    "D:/mazen/EagleVision/projects/test-project/Yolo/people-detection-using-YOLOv11-Deepsort/yolo11s.pt"
)
names = model.model.names

cap = cv2.VideoCapture(
    "D:/mazen/EagleVision/projects/test-project/Yolo/people-detection-using-YOLOv11-Deepsort/People.mp4"
)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

out = cv2.VideoWriter(
    "D:/mazen/EagleVision/projects/test-project/Yolo/people-detection-using-YOLOv11-Deepsort/output.mp4",
    cv2.VideoWriter_fourcc(*"mp4v"),
    fps,
    (width, height),
)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, classes=[0])

    if results[0].boxes is not None:
        boxes = results[0].boxes.xyxy.int().cpu().tolist()

        # Check if tracking IDs exist before attempting to retrieve them
        if results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu.tolist()
        else:
            track_ids = [-1] * len(boxes)  # Use -1 for objects without IDs
        for box, track_id in zip(boxes, track_ids):
            # Iterate through each detected box within the results object
            # Get coordinates (xyxy format)
            x1, y1, x2, y2 = box
            # Draw the rectangle

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

            # Draw the track ID and class label
    out.write(frame)
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
