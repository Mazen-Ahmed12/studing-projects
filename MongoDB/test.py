from numpy import result_type
import pymongo
from pymongo import MongoClient
import sys
import datetime

# --- CONFIGURATION: Use the local connection string ---
# The default local URI is simple and straightforward
MONGODB_URI = "mongodb://localhost:27017/"
DB_NAME = "MongoDB"  # A database name you choose
COLLECTION_NAME = "MongoDB"  # A collection name you choose (like a table)
# ----------------------------------------------------


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


# Example function to insert data
def insert_sample_data():
    print("\n--- 1. CREATE (Insert) ---")

    insert_one_result = {
        "item": "journal",
        "qty": 25,
        "tags": ["blank", "red"],
        "size": {"h": 14, "w": 21, "uom": "cm"},
    }

    # The command to insert a single data document
    result = collection.insert_one(insert_one_result)
    print(f"Inserted document ID: {result.inserted_id}")

    # insert many

    insert_many_results = [
        {
            "item": "canvas",
            "qty": 100,
            "tags": ["cotton"],
            "size": {"h": 28, "w": 35.5, "uom": "cm"},
        },
        {
            "item": "planner",
            "qty": 75,
            "tags": ["blank", "red"],
            "size": {"h": 22, "w": 30, "uom": "cm"},
        },
    ]

    result2 = collection.insert_many(insert_many_results)
    print(f"Inserted document IDs: {result2.inserted_ids}")


def read_sample_data():
    print("\n--- 2. READ (Query) ---")
    query_filter = {"qty": {"$gt": 50}}
    result3 = list(collection.find(query_filter))
    print(f"Found {len(result3)} documents with quantity > 50")
    for res in result3:
        print(res)

    collection.find_raw_batches
    one_item = collection.find_one({"item": "journal"})
    print(f"found one item by name 'journal:{one_item}")


def update_sample_data():
    print("\n--- 3. UPDATE (Modify) ---")
    update_query = {"item": "journal"}
    new_value = {"$set": {"qty": 50, "status": "updated"}}
    result4 = collection.update_one(update_query, new_value)
    print(f"Updated document: {result4}")


def delete_sample_data():
    print("\n--- 4. DELETE ---")
    delete_query = {"qty": {"$gte": 75}}
    result5 = collection.delete_many(delete_query)
    print(f"Deleted documents: {result5.deleted_count}")


def the_final_display():
    print("\n the remaining docs")
    remaining_docs = list(collection.find({}))
    print(f"remaining documets in collection: {remaining_docs}")
    print(f"remaining documets in collection: {len(remaining_docs)}")


if __name__ == "__main__":
    collection = get_mongo_collection()
    insert_sample_data()
    read_sample_data()
    update_sample_data()
    delete_sample_data()
    the_final_display()
