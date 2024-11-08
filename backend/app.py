import logging
import asyncio
import os
from quart import Quart, request
from quart_cors import cors
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from utils.encryption_utils import decrypt_token

from services.course_service import update_student_quiz_data, update_quiz_questions_per_course
from services.video_service import update_course_videos

from routes.base_routes import init_base_routes
from routes.user_routes import init_user_routes
from routes.video_routes import init_video_routes
from routes.support_routes import init_support_routes
from routes.course_routes import init_course_routes

from config import Config

# Set up logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Quart app
app = Quart(__name__)
app = cors(app, allow_origin="https://canvas.instructure.com", allow_headers=["Content-Type", "Authorization"], allow_methods=["GET", "POST", "OPTIONS"])

# Log incoming requests
@app.before_request
async def log_request():
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")

# Initialize routes first
init_base_routes(app)
init_user_routes(app)
init_course_routes(app)
init_video_routes(app)
init_support_routes(app)

# Apply CORS after routes are initialized

# MongoDB setup
HEX_ENCRYPTION_KEY = Config.HEX_ENCRYPTION_KEY
encryption_key = bytes.fromhex(HEX_ENCRYPTION_KEY)
client = AsyncIOMotorClient(Config.DB_CONNECTION_STRING)
db = client[Config.DATABASE]
token_collection = db[Config.TOKENS_COLLECTION]

async def scheduled_update():
    logger.info("Scheduled update started")
    try:
        async for token in token_collection.find():
            courseids = token.get('courseids')
            authkey = Config.DB_CONNECTION_STRING
            access_token = decrypt_token(encryption_key, token.get('auth'))
            link = token.get('link').replace("https://", "").replace("http://", "")
            logger.info("Processing token with link: %s", link)

            if all([courseids, access_token, authkey, link]):
                for course_id in courseids:
                    try:
                        await update_student_quiz_data(course_id, access_token, link)
                        await update_quiz_questions_per_course(course_id, access_token, link)
                        await update_course_videos(course_id)
                        logger.info("Processed course ID: %s", course_id)
                    except Exception as course_error:
                        logger.error("Error processing course ID %s: %s", course_id, course_error)
            else:
                logger.warning("Missing data for token processing: %s", token)
    except Exception as e:
        logger.error("Error in scheduled update: %s", e)

async def schedule_updates():
    while True:
        await scheduled_update()
        await asyncio.sleep(Config.SET_TIMER)  # Config.SET_TIMER for dynamic timing

@app.before_serving
async def startup():
    logger.info("Starting scheduled updates...")
    asyncio.create_task(schedule_updates())  # Start the update loop in the background

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
