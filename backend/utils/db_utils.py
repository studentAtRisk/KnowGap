from pymongo import MongoClient
from config import Config  

def remove_field_from_collection(db_name, collection_name, field_name, uri=""):
    """
    Remove a specified field from all documents in a MongoDB collection.

    Parameters:
    - db_name (str): The name of the database.
    - collection_name (str): The name of the collection.
    - field_name (str): The name of the field to remove.
    - uri (str): MongoDB connection URI (default: "mongodb://localhost:27017").

    Example:
    remove_field_from_collection("my_database", "my_collection", "unnecessary_field")
    """
    # Connect to MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    
    # Remove the specified field from all documents in the collection
    result = collection.update_many({}, {"$unset": {field_name: ""}})
    
    print(f"Removed '{field_name}' from {result.modified_count} documents in '{collection_name}' collection.")
    
    # Close the MongoDB connection
    client.close()

# Example usage
if __name__ == "__main__":
    remove_field_from_collection(
        db_name=Config.DATABASE,
        collection_name="",
        field_name=""
    )
