import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort  # Import the DeepSORT library

# Load your custom YOLOv11 segmentation model
# This model detects and segments plastic waste, providing boxes and masks
model = YOLO('D:/mazen/EagleVision/projects/test-project/Yolo/Fire-And-Smoke-Detection-Using-a-Custom-YOLOv11-Segmentation-Model--main/yolo11s.pt')  # Adjust path

# Initialize DeepSORT tracker with clear parameter explanations
# - max_age: How many frames to keep a track alive if no detection (e.g., occlusion). Set low for fast-moving waste.
# - nn_budget: Limits stored appearance features per track (prevents memory bloat).
# - embedder: 'clip_RN50' is a pre-trained model for extracting visual features (color, shape) of detected objects.
# - max_iou_distance: Max overlap (IoU) for matching detections to tracks (0.7 means 70% overlap threshold).
# - n_init: Frames needed to confirm a new track (avoids tracking noise).
tracker = DeepSort(
    max_age=20,  # Tune: Higher for slower videos, lower for real-time
    nn_budget=200,  # Balance: Higher for more accuracy, but slower
    embedder='clip_RN50',  # Alternative: 'mobilenet' for faster but less accurate
    embedder_gpu=False,
    max_iou_distance=0.5,
    n_init=3  # Requires 3 consecutive detections to start tracking
)

# Video capture: Use webcam (0) or a file path for testing plastic waste videos
cap = cv2.VideoCapture('D:/mazen/EagleVision/projects/test-project/Yolo/Fire-And-Smoke-Detection-Using-a-Custom-YOLOv11-Segmentation-Model--main/People.mp4')  # Or 'path/to/plastic_waste_video.mp4'

fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Frame width
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Frame height

out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# Optional: Track active plastic waste IDs to add logic (e.g., count unique items)
active_tracks = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Step 1: Run YOLOv11 segmentation on the frame
    # This gives detections with boxes, confidences, classes, and masks
    results = model(frame, conf=0.7)  # Adjust confidence to filter weak detections
    
    # Step 2: Format YOLO detections for DeepSORT
    # DeepSORT needs: list of ((left, top, width, height), confidence, class_id)
    # We use bounding boxes from segmentation results (ignores masks for tracking, but we can still draw them later)
    detections = []
    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0].int().cpu().item())  # Class ID (e.g., 0 for 'plastic_waste')
            if cls == 0:  # Filter only for plastic waste; adjust if multiple classes
                x1, y1, x2, y2 = box.xyxy[0].int().cpu().tolist()  # Bounding box coordinates
                conf = box.conf[0].int().cpu().item()  # Detection confidence
                # Convert to ltwh format (left, top, width, height)
                width, height = x2 - x1, y2 - y1
                detections.append(((x1, y1, width, height), conf, cls))
    
    # Step 3: Update DeepSORT with the formatted detections
    # - Pass the current frame: Needed for extracting appearance features (deep part of DeepSORT)
    # - This predicts motion, matches to existing tracks, and creates/deletes tracks as needed
    # - Output: List of Track objects with IDs, boxes, status (confirmed/tentative)
    tracks = tracker.update_tracks(detections, frame=frame)
    
    # Step 4: Process and visualize tracked objects
    # Loop through confirmed tracks only (skip tentative ones to avoid false positives)
    fire_detected = False
    for track in tracks:
        if not track.is_confirmed():  # DeepSORT's internal check: Track is reliable after n_init frames
            continue
        
        track_id = track.track_id  # Unique ID assigned by DeepSORT (persistent across frames)
        ltrb = track.to_ltrb()  # Get updated bounding box (left, top, right, bottom)
        cls = track.det_class  # Class from original detection
        
        # Draw the tracked bounding box and ID on the frame
        x1, y1, x2, y2 = map(int, ltrb)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green for tracked objects
        cv2.putText(frame, f'fire ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Optional: Draw segmentation mask if available (from YOLO results)
        # Match track to original result masks (simplified; use index or IoU matching for precision)
        # For example, if you have masks: cv2.polylines(frame, [mask.xy[0].astype(int)], True, (255, 0, 0), 2)
        
        fire_detected = True
        
        
        # Example Advanced Logic: Track unique plastic items
        if track_id not in active_tracks:
            active_tracks.add(track_id)
            print(f'New fire waste tracked: ID {track_id}')  # Could log or alert here
    
    # Optional: Reset if no detections
    if not fire_detected:
        active_tracks.clear()
    
    out.write(frame)

    
    # Display the frame with tracking
    cv2.imshow('fire Waste Detection with Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()