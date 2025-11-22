from flask import Flask, request, render_template, redirect, url_for
import os, threading
from detection import process_video, process_url, process_live


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

detections_store = []
processing = False


@app.route("/")
def index():
    return render_template(
        "index.html", processing=processing, detections=detections_store
    )


@app.route("/result")
def result():
    return render_template("results.html", detections=detections_store)


@app.route("/upload", methods=["POST"])
def upload_video():
    global processing, detections_store
    file = request.files["video"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    processing = True
    threading.Thread(target=run_detection, args=(filepath, "file")).start()
    return redirect(url_for("index"))


@app.route("/upload_url", methods=["post"])
def upload_url():
    global processing, detections_store
    url = request.form["video_url"]
    processing = True
    threading.Thread(target=run_detection, args=(url, "url")).start()
    return redirect(url_for("index"))


@app.route("/live", methods=["POST"])
def live():
    global processing, detections_store
    processing = True
    threading.Thread(target=run_detection, args=(0, "live")).start()
    return redirect(url_for("index"))


def run_detection(source, mode):
    global processing, detections_store
    if mode == "file":
        detections_store = process_video(source)
    elif mode == "url":
        detections_store = process_url(source)
    elif mode == "live":
        detections_store = process_live(source)
    processing = False


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
# run this first befor running the app
# set KMP_DUPLICATE_LIB_OK=TRUE
# python app.py
