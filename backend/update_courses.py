
from flask import jsonify
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from datetime import datetime, timezone

global_amtofquizzes = 5

async def get_database(connectionString):
    CONNECTION_STRING = connectionString
    client = MongoClient(CONNECTION_STRING)
    # Create/select the database with inputted name
    return client['NoGap']

async def update_quiz_rec(courseid, access_token, dbname, collection_name, current_quiz, link):
    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes/{current_quiz}/statistics'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    question_text = []
                    question_id = []
                    selectors = [[]]
                    noanswerset = ["multiple_choice_question", "true_false_question", "short_answer_question"]
                    answerset = ["fill_in_multiple_blanks_question", "multiple_dropdowns_question", "matching_question"]

                    for x in range(len(data["quiz_statistics"][0]["question_statistics"])):
                        question_text.append(BeautifulSoup(data["quiz_statistics"][0]["question_statistics"][x]["question_text"], features="html.parser").get_text())
                        question_text[x] = clean_text(question_text[x])
                        question_id.append(data["quiz_statistics"][0]["question_statistics"][x]["id"])
                        selectors.append([])

                        if data["quiz_statistics"][0]["question_statistics"][x]["question_type"] in noanswerset:
                            for y in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answers"])):
                                if not data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["correct"]:
                                    selectors[x] += data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["user_ids"] or [-1]

                        if data["quiz_statistics"][0]["question_statistics"][x]["question_type"] in answerset:
                            for z in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"])):
                                for y in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"])):
                                    if not data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["correct"]:
                                        selectors[x] += data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["user_ids"] or [-1]

                    return question_text, selectors, question_id
                else:
                    return {'error': f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        return {'error': f'Failed to grab quiz statistics due to: {str(e)}'}, 500

async def get_quizzes(courseid, access_token, link):
    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes?per_page=100'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    unfiltered_data = await response.json()
                    max_date = datetime.now(timezone.utc)
                    data = sorted(
                        [item for item in unfiltered_data if item["published"] and (item["unlock_at"] is None or parse_date(item["unlock_at"]) <= max_date)],
                        key=lambda x: parse_date(x["unlock_at"]) if x["unlock_at"] else datetime.min.replace(tzinfo=timezone.utc),
                        reverse=True
                    )

                    quizlist = []
                    quizname = []
                    for x in range(min(len(data), global_amtofquizzes)):
                        quizlist.append(data[x]["id"])
                        quizname.append(data[x]["title"])
                    return quizlist, quizname
                else:
                    return {'error': f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        return {'error': str(e)}, 500

async def update_db(courseid, access_token, connectionString, link):
    dbname = await get_database(connectionString)
    quiz_collection = dbname["Quiz Questions"] 
    student_collection = dbname["Students"]  

    quizlist, quizname = await get_quizzes(courseid, access_token, link)
    
    api_url = f'https://{link}/api/v1/courses/{courseid}/enrollments'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    studentmap = {}
                    course_name = await get_course_details(courseid, access_token, link)

                    for x in range(len(quizlist)):
                        question_text, selectors, question_id = await update_quiz_rec(courseid, access_token, dbname, quiz_collection, quizlist[x], link)

                        # Update students and quiz questions
                        for y in range(len(selectors)):
                            for student_id in selectors[y]:
                                # Only process valid student IDs
                                if student_id != -1:  
                                    question_info = {
                                        "question": question_text[y],
                                        "questionid": question_id[y]
                                    }

                                    # Update student map
                                    if student_id in studentmap:
                                        quiz_found = False
                                        for quiz in studentmap[student_id]:
                                            if quiz['quizname'] == quizname[x]:
                                                existing_questions = {q['questionid'] for q in quiz['questions']}
                                                if question_info['questionid'] not in existing_questions:
                                                    quiz['questions'].append(question_info)
                                                quiz_found = True
                                                break

                                        if not quiz_found:
                                            studentmap[student_id].append({
                                                "quizname": quizname[x],
                                                "quizid": quizlist[x],
                                                "questions": [question_info],
                                                "used": False
                                            })
                                    else:
                                        studentmap[student_id] = [{
                                            "quizname": quizname[x],
                                            "quizid": quizlist[x],
                                            "questions": [question_info],
                                            "used": False
                                        }]

                        # Save quiz questions to the "Quiz Questions" collection
                        for y in range(len(question_text)):
                            try:
                                quiz_collection.update_one(
                                    {'quizid': quizlist[x], 'courseid': str(courseid), "course_name": course_name, "questionid": str(question_id[y])},
                                    {"$set": {"question_text": question_text[y]}},
                                    upsert=True
                                )
                            except Exception as e:
                                print("Error updating quiz questions:", e)

                    # Use studentmap to update Students
                    for key in studentmap.keys():
                        try:
                            student_collection.update_one({'_id': str(key)}, {"$set": {str(courseid): studentmap[key]}}, upsert=True)
                        except Exception as e:
                            print("Error updating student data:", e)

    except Exception as e:
        print("Error:", e)
    return 1

async def get_course_details(courseid, access_token, link):
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
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        # Normalize to UTC
        return dt.astimezone(timezone.utc)
    return None

def clean_text(text):
    # Normalize and filter to keep only ASCII characters
    return ''.join(char for char in text if ord(char) < 128)


async def main():
    courseid = 1425706
    access_token = '1158~ZENrewhnRzFkMLhxQDP47U9NcrX6exWeT8eGXKW4z2X7yy36RFDcMB3C6tJk4fha'
    connectionString = "mongodb+srv://jordan917222:PPJjEItclZaEECv7@studentsatrisk.ptqdmcu.mongodb.net/"
    link = 'webcourses.ucf.edu'
    await update_db(courseid, access_token, connectionString, link)
    print("Updated quiz questions for this course")

if __name__ == "__main__":
    asyncio.run(main())