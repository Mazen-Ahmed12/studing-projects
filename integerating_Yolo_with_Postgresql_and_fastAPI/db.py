import psycopg
from datetime import datetime
import sys


async def save_detection(filename, detections):
    try:
        async with await psycopg.AsyncConnection.connect(
            dbname="yolo_db", user="postgres", password="mazen", host="localhost"
        ) as conn:

            async with conn.cursor() as cur:
                data_to_insert = []
                for d in detections:
                    data_to_insert.append(
                        (
                            filename,
                            datetime.now(),
                            d.get("track_id"),
                            d.get("frame_id"),
                            d.get("fall_message"),
                        )
                    )

                await cur.executemany(
                    "INSERT INTO detections (filename, timestamp, track_id, frame_id, fall_message) VALUES (%s, %s, %s, %s, %s)",
                    data_to_insert,
                )

                await conn.commit()
                print(f"Successfully saved {cur.rowcount} detections.")

    except psycopg.DatabaseError as e:
        print(f"[DB Error] A database error occurred {e}", file=sys.stderr)
        raise e
