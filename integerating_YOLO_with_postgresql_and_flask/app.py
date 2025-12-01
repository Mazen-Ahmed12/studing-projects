from flask import Flask, request, render_template, redirect, url_for
import os, threading, sys
import psycopg
from detection import process_video, process_url, process_live

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

detections_store = []
processing = False

DB_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "mazen",
    "dbname": "postgres",
}


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


def save_detection_results(video_source, detections_store):
    INSERT_SQL = "INSERT INTO detections (video_source, track_id, frame_id, fall_message) VALUES (%s, %s, %s, %s);"
    if detections_store:
        print(
            f"\n inserting {len(detections_store)} fall detections data into database"
        )
        for detection in detections_store:
            execute_sql(
                INSERT_SQL,
                data=(
                    video_source,
                    detection["track_id"],
                    detection["frame_id"],
                    detection["fall_message"],
                ),
            )
        print("insertion done")
    else:
        print("no falls detected in this video.")


@app.route("/")
def index():
    return render_template("index.html", processing=processing)


@app.route("/result")
def result():
    SELECT_SQL = (
        "SELECT track_id, frame_id, fall_message FROM detections ORDER BY frame_id ASC;"
    )
    detection_list = execute_sql(SELECT_SQL, fetch_results=True)
    return render_template("results.html", detections=detection_list)


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

    save_detection_results(video_source=source, detections_store=detections_store)
    processing = False


if __name__ == "__main__":
    execute_sql(
        """
     CREATE TABLE IF NOT EXISTS detections(
        id SERIAL PRIMARY KEY,
        video_source TEXT NOT NULL,
        track_id INTEGER NOT NULL,
        frame_id INTEGER NOT NULL,
        fall_message TEXT NOT NULL,
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""
    )
    app.run(host="127.0.0.1", port=5000, debug=True)
