from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# Set up async MongoDB connection
client = AsyncIOMotorClient(Config.DB_CONNECTION_STRING)
db = client[Config.DATABASE]
course_contexts_collection = db[Config.CONTEXTS_COLLECTION]


async def update_context(course_id, course_context):
    """Updates or inserts the course context for a specific course."""
    try:
        # Update or insert the course context document
        result = await course_contexts_collection.update_one(
            {'courseid': course_id},
            {
                '$set': {
                    'courseid': course_id,
                    'course_context': course_context,
                }
            },
            upsert=True
        )
        return {
            'status': 'Success' if result.modified_count > 0 or result.upserted_id else 'No changes made',
            'message': 'Course context updated successfully' if result.modified_count > 0 or result.upserted_id else 'No updates applied'
        }
    except Exception as e:
        return {'status': 'Error', 'message': str(e)}
