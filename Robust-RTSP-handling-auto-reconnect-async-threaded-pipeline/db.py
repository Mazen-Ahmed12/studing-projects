# db.py
from motor.motor_asyncio import AsyncIOMotorClient
import datetime

client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")
db = client.yolo_db
collection = db.live_detections


async def save_fall(d):
    d["timestamp"] = datetime.datetime.now()
    try:
        result = await collection.insert_one(d)
        print(f"[DB] Saved fall → ID: {result.inserted_id} | Track {d.get('track_id')}")
    except Exception as e:
        print(f"[DB] ERROR: {e}")
