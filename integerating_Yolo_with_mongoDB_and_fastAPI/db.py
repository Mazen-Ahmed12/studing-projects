import datetime
import pymongo
from pymongo import MongoClient


MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "yolo_db"
COLLECTION_NAME = "yolo_db"


def get_mongo_collection():
    """Establishes local MongoDB connection and returns the collection object."""
    try:
        # Connect to the local server
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        print(f"MongoDB local connection successful.")
        return collection
    except pymongo.errors.ConnectionFailure as e:
        print(f"Failed to connect to local MongoDB server: {e}")
        print("Ensure your local 'mongod' server is running in the background.")
        sys.exit(1)


def insert_detection(filename, detections):
    collection = get_mongo_collection()
    if detections:
        documents_to_insert = [
            {"filename": filename, **d, "timestamp": datetime.datetime.now()}
            for d in detections
        ]

        result = collection.insert_many(documents_to_insert)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")
    else:
        print("No detections to save.")

    collect = collection.find()
    for document in collect:
        print(f"display the detection data {document}")
