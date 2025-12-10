import cv2, asyncio, threading, time
from concurrent.futures import ThreadPoolExecutor
from detection import detect_falls_in_frame
from db import save_fall
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

RTSP_URL = "rtsp://localhost:5544/stream"

executor = ThreadPoolExecutor(max_workers=2)


class RTSPCapture:
    def __init__(self, url):
        self.url = url
        self.cap = None
        self.lock = threading.Lock()
        self.on = True

    async def start(self):
        while self.on:
            try:
                with self.lock:
                    if not self.cap or not self.cap.isOpened():
                        print(f"[RTSP] Connecting to {self.url}")
                        self.cap = cv2.VideoCapture(self.url)
                        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        self.cap.set(cv2.CAP_PROP_FPS, 25)
                        if not self.cap.isOpened():
                            raise Exception("Failed to open stream")
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    yield frame
                else:
                    raise Exception("No frame read")
            except Exception as e:
                print(f"[RTSP] ERROR → reconnecting: {e}")
                with self.lock:
                    if self.cap:
                        self.cap.release()
                        self.cap = None
                await asyncio.sleep(3)

    def stop(self):
        self.on = False
        with self.lock:
            if self.cap:
                self.cap.release()


async def rtsp_generator():
    cap = RTSPCapture(RTSP_URL)
    frame_id = 0
    try:
        async for frame in cap.start():
            frame_id += 1

            annotated_frame, falls = await asyncio.get_event_loop().run_in_executor(
                executor, detect_falls_in_frame, frame, frame_id
            )

            for f in falls:
                await save_fall(f)

            if annotated_frame is not None:
                _, buf = cv2.imencode(".jpg", annotated_frame)
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            else:
                print(f"[RTSP] Skipping empty frame {frame_id}")

            if frame_id % 30 == 0:
                print(f"[RTSP] Frame {frame_id} processed successfully")

    finally:
        cap.stop()
        executor.shutdown()
