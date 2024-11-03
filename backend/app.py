import logging
import asyncio
import os
from quart import Quart
from quart_cors import cors
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from utils.encryption_utils import at_risk_encrypt_token, at_risk_decrypt_token

from services.course_service import update_student_quiz_data
from services.course_service import update_quiz_questions_per_course #(replace these with whatever the update_db portion is)

from routes.base_routes import init_base_routes
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
# cors(app, 
#      allow_origin=["https://canvas.instructure.com"],
#      allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
#      allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
#      allow_credentials=True)
cors(app, allow_origin="*")
app = Quart(__name__)
# Initialize routes
init_base_routes(app)
init_course_routes(app)
init_video_routes(app)
init_support_routes(app)

app = cors(app, allow_origin="https://canvas.instructure.com", allow_headers=["Content-Type", "Authorization"])

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
            access_token = at_risk_decrypt_token(encryption_key, token.get('auth'))
            link = token.get('link').replace("https://", "").replace("http://", "")
            logger.info("Processing token...")

            if all([courseids, access_token, authkey, link]):
                for course_id in courseids:
                    await update_student_quiz_data(course_id, access_token, link)
                    await update_quiz_questions_per_course(course_id, access_token, link)
                logger.info("Processed course IDs: %s", courseids)
    except Exception as e:
        logger.error("Error in scheduled update: %s", e)

async def schedule_updates():
    while True:
        await scheduled_update()
        await asyncio.sleep(Config.SET_TIMER)  # Wait for 10 minutes

@app.before_serving
async def startup():
    logger.info("Starting scheduled updates...")
    asyncio.create_task(schedule_updates())  # Start the update loop


if __name__ == "__main__":
    app.run(debug=True)
