from ultralytics import YOLO
import os
import cv2
import pymongo
from pymongo import MongoClient
import sys
import datetime

# Configuration
MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "MongoDB"
COLLECTION_NAME = "MongoDB"

model = YOLO(
    "D:/mazen/EagleVision/projects/studing-projects/integeration_YOLO_with_mongoDB/yolov11s.pt"
)

detections = []
VIDEO_PATH = "D:/mazen/EagleVision/projects/studing-projects/integeration_YOLO_with_mongoDB/fall.mp4"


def process_video(video_path):
    print(f"[INFO] Trying to open video: {video_path}")

    if not os.path.exists(video_path):
        print(f"[ERROR] Video file not found: {video_path}")
        return []

    cap = cv2.VideoCapture(video_path)  # ← Use video_path directly!
    if not cap.isOpened():
        print("[ERROR] Cannot open video with OpenCV. Wrong codec or corrupted file?")
        return []

    frame_id = 0

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


def get_mongo_collection():
    """Establishes local MongoDB connection and returns the collection object."""
    try:
        # Connect to the local server
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"MongoDB local connection successful.")
        return collection
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to local MongoDB server: {e}")
        print("Ensure your local 'mongod' server is running in the background.")
        sys.exit(1)


def save_detection_data():
    collection = get_mongo_collection()
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} existing documents.")

    process_video(VIDEO_PATH)

    print("\n--- 1. CREATE (Insert) ---")
    global detections
    for detection in detections:
        insert_detection = {
            "track_id": float(detection["track_id"]),
            "frame_id": float(detection["frame_id"]),
            "fall_message": str(detection["fall_message"]),
            "detected_at": datetime.datetime.now(),
        }
        collection.insert_one(insert_detection)
    print("insertion done")

    collect = collection.find()
    for document in collect:
        print(f"display the detection data {document}")


if __name__ == "__main__":
    save_detection_data()
