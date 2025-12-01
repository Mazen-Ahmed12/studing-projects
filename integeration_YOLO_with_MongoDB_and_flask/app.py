from flask import Flask, request, render_template, redirect, url_for
import os, threading, sys
import pymongo
from pymongo import MongoClient
from detection import process_video, process_url, process_live

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

detections_store = []
processing = False

MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "falls"
COLLECTION_NAME = "falls"


def get_mongo_collection():
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"MongoDB local connection successful.")
        return collection
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to local MongoDB server: {e}")
        print("Ensure your local 'mongod' server is running in the background.")
        sys.exit(1)


@app.route("/")
def index():
    return render_template("index.html", processing=processing)


@app.route("/result")
def result():
    collection = get_mongo_collection()
    detections_store = collection.find_one(sort=[("_id", -1)])
    print(detections_store)
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

    single_document = {
        "video_source": source,
        "detections_list": detections_store,
    }
    collection.insert_one(single_document)
    print("insertion done")

    processing = False


if __name__ == "__main__":

    collection = get_mongo_collection()
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} existing documents.")

    app.run(host="127.0.0.1", port=5000, debug=True)
