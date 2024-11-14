import asyncio
import aiohttp
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from config import Config
async def get_course_name(courseid, access_token, link):
    api_url = f'https://{link}/api/v1/courses/{courseid}'
    headers = {'Authorization': f'Bearer {access_token}'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    course_details = await response.json()
                    course_name = course_details.get("name", "Course name not found")
                    return course_name
                else:
                    print(f"Failed to retrieve course. Status code: {response.status}")
    except Exception as e:
        return {'error': str(e)}, 500
def parse_date(date_str):
    """Parses a date string to UTC datetime."""
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(timezone.utc)  # Normalize to UTC
    return None
def clean_text(text):
    """Normalizes text and filters to keep only ASCII characters."""
    return ''.join(char for char in text if ord(char) < 128)
def get_incorrect_user_ids(question, no_answer_set, answer_set):
    """Extracts user IDs for incorrect answers based on question type."""
    incorrect_user_ids = []
    if question["question_type"] in no_answer_set:
        incorrect_user_ids = extract_no_answer_user_ids(question["answers"])
    elif question["question_type"] in answer_set:
        incorrect_user_ids = extract_answer_set_user_ids(question["answer_sets"])
    return incorrect_user_ids if incorrect_user_ids else [-1]
def extract_no_answer_user_ids(answers):
    """Helper to gather user IDs from questions without answer sets."""
    return [user_id for answer in answers if not answer["correct"]
            for user_id in (answer.get("user_ids") or [-1])]
def extract_answer_set_user_ids(answer_sets):
    """Helper to gather user IDs from questions with answer sets."""
    user_ids = []
    for answer_set in answer_sets:
        user_ids.extend(user_id for answer in answer_set["answers"] if not answer["correct"]
                        for user_id in (answer.get("user_ids") or [-1]))
    return user_ids
async def get_quizzes(courseid, access_token, link, max_quizzes=10):
    """
    Fetches a list of quizzes for a course, filtered by published status and unlock date.
    Returns a sorted list of quiz IDs and quiz titles in descending order by unlock date.
    """
    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes?per_page=100'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    unfiltered_data = await response.json()
                    max_date = datetime.now(timezone.utc)  # Current time in UTC
                    
                    filtered_data = [
                        quiz for quiz in unfiltered_data
                        if quiz["published"] and (
                            # If 'unlock_at' is None or empty, treat it as the Unix epoch (earliest possible date)
                            (quiz["all_dates"][0]["unlock_at"] and parse_date(quiz["all_dates"][0]["unlock_at"])) or
                            # If 'unlock_at' is None or empty, use the Unix epoch
                            datetime(1970, 1, 1, tzinfo=timezone.utc)
                        ) <= max_date
                    ]

                    # Sort by unlock date in descending order (newest first)
                    sorted_data = sorted(
                        filtered_data,
                        key=lambda x: (
                            # If 'unlock_at' is None or empty, treat it as the Unix epoch (earliest possible date)
                            parse_date(x["all_dates"][0]["unlock_at"]) if x["all_dates"][0]["unlock_at"] else datetime(1970, 1, 1, tzinfo=timezone.utc)
                        ),
                        reverse=True
                    )
                    
                    # Limit to the specified max number of quizzes
                    quiz_list = [quiz["id"] for quiz in sorted_data[:max_quizzes]]
                    quiz_names = [quiz["title"] for quiz in sorted_data[:max_quizzes]]
                    
                    # Debug prints to check output
                    #print("this happens twice? what?")
                    #print("Quiz Names:", quiz_names)
                    return quiz_list, quiz_names
                
                else:
                    error_text = await response.text()
                    print("API Error:", error_text)
                    return {'error': f'Failed to fetch data from API: {error_text}'}, response.status
    
    except Exception as e:
        print("Exception occurred:", str(e))
        return {'error': str(e)}, 500
async def get_question_data(courseid, quiz_id, access_token, link):

    """Fetches question data for a specific quiz, including question text and IDs."""
    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes/{quiz_id}/questions'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    question_texts = [clean_text(BeautifulSoup(q["question_text"], "html.parser").get_text()) for q in data]
                    question_ids = [q["id"] for q in data]
                    return question_texts, question_ids
                else:
                    error_text = await response.text()
                    return {'error': f'Failed to fetch questions: {error_text}'}, response.status
    except Exception as e:
        return {'error': str(e)}, 500