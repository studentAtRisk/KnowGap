from pymongo import MongoClient
from config import Config  

client = MongoClient(Config.DB_CONNECTION_STRING)
db = client[Config.DATABASE]

def remove_field_from_collection(collection_name, field_name):
    """
    Remove a specified field from all documents in a MongoDB collection.

    Parameters:
    - collection_name (str): The name of the collection.
    - field_name (str): The name of the field to remove.

    Example:
    remove_field_from_collection("my_collection", "unnecessary_field")
    """
    collection = db[collection_name]
    
    # Remove the specified field from all documents in the collection
    result = collection.update_many({}, {"$unset": {field_name: ""}})
    
    print(f"Removed '{field_name}' from {result.modified_count} documents in '{collection_name}' collection.")
    
    # Close the MongoDB connection
    #client.close()

def find_documents_by_field(collection_name, field_name, search_value):
    """
    Find documents in a MongoDB collection where a specified field matches a given value.

    Parameters:
    - collection_name (str): The name of the collection.
    - field_name (str): The name of the field to search by.
    - search_value: The value to match for the specified field.

    Returns:
    - list: A list of documents where the field matches the specified value.
    
    Example:
    find_documents_by_field("my_collection", "username", "johndoe")
    """
    collection = db[collection_name]
    
    # Query for documents where the field matches the search value
    query = {field_name: search_value}
    documents = list(collection.find(query))
    
    print(f"Found {len(documents)} document(s) in '{collection_name}' collection where '{field_name}' is '{search_value}'.")
    
    # Close the MongoDB connection
    #client.close()
    
    return documents



# Example usage
if __name__ == "__main__":
    remove_field_from_collection(
        db_name=Config.DATABASE,
        collection_name="",
        field_name=""
    )
