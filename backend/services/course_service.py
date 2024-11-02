from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from utils.course_utils import (
    parse_date, clean_text, get_incorrect_user_ids, get_quizzes
)
import aiohttp
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
client = AsyncIOMotorClient(Config.DB_CONNECTION_STRING)
db = client[Config.DATABASE]
course_contexts_collection = db[Config.CONTEXTS_COLLECTION]
students_collection = db[Config.STUDENTS_COLLECTION]

async def update_context(course_id, course_context):
    """Updates or inserts the course context for a specific course."""
    try:
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
        status = 'Success' if result.modified_count > 0 or result.upserted_id else 'No changes made'
        return {'status': status, 'message': 'Course context updated successfully' if status == 'Success' else 'No updates applied'}
    except Exception as e:
        logger.error("Error updating course context: %s", e)
        return {'status': 'Error', 'message': str(e)}

async def get_incorrect_question_data(courseid, currentquiz, link):
    """Fetches incorrect answer data for a specific quiz."""
    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes/{currentquiz}/statistics'
    headers = {'Authorization': f'Bearer {Config.CANVAS_API_KEY}'}
    no_answer_set = {"multiple_choice_question", "true_false_question", "short_answer_question"}
    answer_set = {"fill_in_multiple_blanks_question", "multiple_dropdowns_question", "matching_question"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("Failed to fetch quiz statistics: %s", error_text)
                    return {'error': f'Failed to fetch data from API: {error_text}'}, response.status
                
                data = await response.json()
                question_data = data.get("quiz_statistics", [{}])[0].get("question_statistics", [])
                question_texts, question_ids, selectors = [], [], []
                
                for question in question_data:
                    cleaned_text = BeautifulSoup(question["question_text"], "html.parser").get_text()
                    question_texts.append(clean_text(cleaned_text))
                    question_ids.append(question["id"])
                    selectors.append(get_incorrect_user_ids(question, no_answer_set, answer_set))
                
                return [question_texts, selectors, question_ids]
    except Exception as e:
        logger.error("Error fetching incorrect question data: %s", e)
        return {'error': f'Failed to grab quiz statistics due to: {str(e)}'}, 500

async def update_db(courseid, connection_string, link):
    """Updates the database with quiz information and failed questions per student."""
    dbname = AsyncIOMotorClient(connection_string)[Config.DATABASE]
    collection_name = dbname["Students"]
    quizlist, quizname = await get_quizzes(courseid, link)

    api_url = f'https://{link}/api/v1/courses/{courseid}/enrollments'
    headers = {'Authorization': f'Bearer {Config.CANVAS_API_KEY}'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("Failed to fetch enrollments: %s", error_text)
                    return {'error': f'Failed to fetch enrollments: {error_text}'}, response.status

                data = await response.json()
                studentmap = {}

                for i, quiz_id in enumerate(quizlist):
                    results = await get_incorrect_question_data(courseid, quiz_id, link)
                    if isinstance(results, dict) and 'error' in results:
                        return results  # Propagate the error if fetching quiz data fails
                    
                    question_texts, selectors, question_ids = results

                    for j, user_ids in enumerate(selectors):
                        for student_id in user_ids:
                            if student_id != -1:
                                question_info = {"question": question_texts[j], "questionid": question_ids[j]}
                                if student_id in studentmap:
                                    quiz_found = False
                                    for quiz in studentmap[student_id]:
                                        if quiz['quizname'] == quizname[i]:
                                            existing_questions = {q['questionid'] for q in quiz['questions']}
                                            if question_info['questionid'] not in existing_questions:
                                                quiz['questions'].append(question_info)
                                            quiz_found = True
                                            break
                                    if not quiz_found:
                                        studentmap[student_id].append({
                                            "quizname": quizname[i],
                                            "quizid": quiz_id,
                                            "questions": [question_info],
                                            "used": False
                                        })
                                else:
                                    studentmap[student_id] = [{
                                        "quizname": quizname[i],
                                        "quizid": quiz_id,
                                        "questions": [question_info],
                                        "used": False
                                    }]
                
                # Save to database
                for student_id, quizzes in studentmap.items():
                    try:
                        collection_name.update_one(
                            {'_id': str(student_id)},
                            {"$set": {str(courseid): quizzes}},
                            upsert=True
                        )
                    except Exception as e:
                        logger.error("Error updating database for student %s: %s", student_id, e)
    except Exception as e:
        logger.error("Error in update_db: %s", e)
        return {'error': str(e)}, 500
    return {'status': 'Success', 'message': 'Database update completed successfully'}
