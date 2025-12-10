from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import uvicorn
from rtsp_live import rtsp_generator

app = FastAPI(title="robust Rtsp Live Fall Detection")


@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>robust Rtsp Live Fall Detection</h1><img src='/live' width='960'>"


@app.get("/live")
def live():
    return StreamingResponse(
        rtsp_generator(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
