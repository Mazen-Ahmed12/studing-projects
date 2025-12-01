CREATE TABLE detections (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    timestamp TIMESTAMP,
    track_id FLOAT,
    frame_id FLOAT,
    fall_message TEXT
);
