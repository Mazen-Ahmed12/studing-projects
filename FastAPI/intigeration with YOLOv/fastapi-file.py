import cv2
import torch
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
import os
import shutil
from ultralytics import YOLO

# This temporarily sets the environment variable KMP_DUPLICATE_LIB_OK to TRUE for your current command session, which suppresses the Error #15 and allows the program to run past that conflict.
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = YOLO("yolov11s.pt").to(device)


@app.get("/cuda-status")
def cuda_status():
    return {
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "gpu_name": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only"
        ),
    }


@app.post("/detect")
def detect(file: UploadFile = File(...)):

    video_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

    # Process the image using YOLO
    results = model.track(
        source=video_path, persist=True, classes=[0], verbose=False, stream=True
    )

    fall_detected = False
    fall_details = []
    frame_count = 0

    for result in results:
        frame_count += 1

        for box in result.boxes:
            boxes = box.xyxy.cpu().numpy()
            track_ids = box.id.cpu().numpy() if box.id is not None else []

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                height = y2 - y1
                width = x2 - x1

                if height - width < 0:
                    fall_detected = True
                    fall_details.append(
                        f"FALL DETECTED: Track ID {track_id} in Frame {frame_count}. Aspect Ratio (H-W) < 0."
                    )

    os.remove(video_path)

    if fall_detected:
        return {
            "status": "Alert Triggered",
            "message": "Multiple fall events were detected in the video.",
            "incidents": fall_details,
        }
    else:
        return {
            "status": "Safe",
            "message": "No fall events detected for the 'person' class.",
        }
