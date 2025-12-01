from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from yolo_detector import process_video
from db import insert_detection
import torch

app = FastAPI()


@app.get("/")
def hello():
    return "hello"


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
async def detect(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400, detail="Uploaded file must have a filename"
        )
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    results = process_video(temp_path)
    insert_detection(file.filename, results)
    print("Detection completed successfully")
    return {"filename": file.filename, "detections": results}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
