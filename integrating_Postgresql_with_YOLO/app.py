from datetime import datetime
import cv2
from ultralytics import YOLO
import os
import psycopg
import sys

# configuration : dont forget to change thosr params to your actual credentials
DB_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "mazen",
    "dbname": "postgres",
}
# the detection funtion
# This temporarily sets the environment variable KMP_DUPLICATE_LIB_OK to TRUE for your current command session, which suppresses the Error #15 and allows the program to run past that conflict.
model = YOLO(
    "D:/mazen/EagleVision/projects/studing-projects/integrating_Postgresql_with_YOLO/yolov11s.pt"
)

detections = []
VIDEO_PATH = "D:/mazen/EagleVision/projects/studing-projects/integrating_Postgresql_with_YOLO/fall.mp4"


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


# the database functions
def execute_sql(sql_query, data=None, fetch_results=False):
    results = None
    try:
        with psycopg.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query, data)

                if fetch_results:
                    results = cur.fetchall()
                    print(f"[DB Action] Fetched {len(results)} rows")
                else:
                    conn.commit()
                    print(f"[DB Action] executed query, Rows affected: {cur.rowcount}")
    except psycopg.DatabaseError as e:
        print(f"[DB Error] A database error occured {e}")
        sys.exit(1)
    return results


if __name__ == "__main__":
    print("--- Starting Database Operations ---")

    # create the database
    print("\nAttempting to create 'detections' table...")
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS detections(
        id SERIAL PRIMARY KEY,
        track_id INTEGER NOT NULL,
        frame_id INTEGER NOT NULL,
        fall_message TEXT NOT NULL,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    execute_sql(CREATE_TABLE_SQL)
    print("table created")

    # 2 call detection funcion
    print("start video processing")
    process_video(VIDEO_PATH)

    # 3 insert Detection data into the database
    INSERT_SQL = (
        "INSERT INTO detections (track_id, frame_id, fall_message) VALUES (%s, %s, %s);"
    )
    if detections:
        print(f"\n inserting {len(detections)} fall detections data into database")
        for detection in detections:
            execute_sql(
                INSERT_SQL,
                data=(
                    detection["track_id"],
                    detection["frame_id"],
                    detection["fall_message"],
                ),
            )
        print("insertion done")
    else:
        print("no falls detected in this video.")

    # 4 show data from database
    print("\nFetching all detections data from database...")
    SELECT_SQL = "SELECT track_id, frame_id, fall_message FROM detections ORDER BY last_updated ASC;"

    detection_list = execute_sql(SELECT_SQL, fetch_results=True)
    if detection_list:
        print("detections list:")
        for track_id, frame_id, fall_message in detection_list:
            print(
                f"Track ID: {track_id}, Frame ID: {frame_id}, Fall Message: {fall_message}"
            )
    else:
        print("no fall detections found in the database.")
