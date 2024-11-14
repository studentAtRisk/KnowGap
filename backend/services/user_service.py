from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from utils.encryption_utils import encrypt_token, decrypt_token

# Async MongoDB connection
client = AsyncIOMotorClient(Config.DB_CONNECTION_STRING)
db = client[Config.DATABASE]
tokens_collection = db[Config.TOKENS_COLLECTION]

async def get_user(user_id):
    """Retrieve a user's data, decrypting the token."""
    user = await tokens_collection.find_one({'_id': user_id})
    if not user: 
        return None

    decrypted_token = decrypt_token(Config.HEX_ENCRYPTION_KEY, user['auth'])
    return {
        "_id": user["_id"],
        "auth": decrypted_token,
        "courseids": user["courseids"],
        "link": user["link"]
    }

async def add_user(user_id, access_token, course_ids, link):
    """Add or update a user token in the database."""
    encrypted_token = encrypt_token(bytes.fromhex(Config.HEX_ENCRYPTION_KEY), access_token)

    await tokens_collection.update_one(
        {'_id': user_id},
        {"$set": {"auth": encrypted_token, "courseids": course_ids, "link": link}}, 
        upsert=True
    )

    # return updated user details
    updated_user = await tokens_collection.find_one({'_id': user_id}, {'_id': 0})
    return updated_user
