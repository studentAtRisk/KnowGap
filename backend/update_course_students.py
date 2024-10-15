
from flask import jsonify
import requests
from pymongo import MongoClient
from pandas import DataFrame
import datetime
from bs4 import BeautifulSoup
import asyncio
import aiohttp
global_amtofquizzes = 5

async def get_database(connectionString):
 
   # connection to database string. Change this to switch databases
   CONNECTION_STRING = connectionString

   client = MongoClient(CONNECTION_STRING)
 
   # create/select the database with inputted name
   return client['NoGap']

async def update_quiz_rec(courseid, access_token, dbname, collection_name, currentquiz, link):



    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes/{currentquiz}/statistics'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }


    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    questiontext = []
                    questionid = []
                    selectors = [[]]
                    noanswerset = ["multiple_choice_question", "true_false_question", "short_answer_question"]
                    answerset = ["fill_in_multiple_blanks_question", "multiple_dropdowns_question", "matching_question"]
                    

                    
                    for x in range(len(data["quiz_statistics"][0]["question_statistics"])):
                        # Clean text to not have any HTML markup
                        questiontext.append(BeautifulSoup(data["quiz_statistics"][0]["question_statistics"][x]["question_text"], features="html.parser").get_text())
                        questiontext[x] = clean_text(questiontext[x])

                        questionid.append(data["quiz_statistics"][0]["question_statistics"][x]["id"])
                        selectors.append([])
                        if data["quiz_statistics"][0]["question_statistics"][x]["question_type"] in noanswerset:
                            for y in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answers"])):

                                if(data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["correct"] == False):
                                    if(len(data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["user_ids"]) > 0):

                                        selectors[x] += data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["user_ids"]
                                    else:
                                        selectors[x] += [-1]
                        if data["quiz_statistics"][0]["question_statistics"][x]["question_type"] in answerset:
                            for z in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"])):
                                for y in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"])):

                                    if(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["correct"] == False):
                                        if(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["user_ids"]) > 0):

                                            selectors[x] += data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["user_ids"]
                                        else:
                                            selectors[x] += [-1]                

                    return [questiontext, selectors, questionid]

                else:
                    print("error")
                    return {'error'f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        return {'error : Failed to grab quiz statistics due to': str(e)}, 500


async def get_quizzes(courseid, access_token, link):


    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes?per_page=100'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    quizlist = []
                    quizname = []
                    for x in range(min(len(data), global_amtofquizzes)):
                        quizlist.append(data[x]["id"])
                        quizname.append(data[x]["title"])
                    print("DONE!")
                    return quizlist, quizname 
                else:
                    return {'error': f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        return {'error': str(e)}, 500


    
#it starts here
async def update_db(courseid, access_token, connectionString, link):


    dbname = await get_database(connectionString)
    # Makes collection with inputted name
    collection_name = dbname["Students"]


    quizlist, quizname = await get_quizzes(courseid,access_token, link)

    api_url = f'https://{link}/api/v1/courses/{courseid}/enrollments'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    studentmap = {}
                    


                # Update quiz topics

                for x in range(len(quizlist)):
                    results = await update_quiz_rec(courseid, access_token, dbname, collection_name, quizlist[x], link)
                    for y in range(len(results[1])):

                        for z in range(len(results[1][y])):
                            if results[1][y][z] != -1:
                                student_id = results[1][y][z]
                                question = results[0][y]
                                questionid = results[2][y]

                                # Create a unique question identifier 
                                question_info = {
                                    "question": question,
                                    "questionid": questionid
                                }

                                # If student already has an entry in studentmap
                                if student_id in studentmap:
                                    # Check if current quizname[x] already exists in the student's failed_questions list
                                    quiz_found = False
                                    for quiz in studentmap[student_id]:
                                        if quiz['quizname'] == quizname[x]:
                                            # Use a set to avoid duplicates
                                            existing_questions = {q['questionid'] for q in quiz['questions']}
                                            if question_info['questionid'] not in existing_questions:
                                                quiz['questions'].append(question_info)
                                            quiz_found = True
                                            break

                                    # If the quiz doesn't exist, add a new entry for this quiz
                                    if not quiz_found:
                                        studentmap[student_id].append({
                                            "quizname": quizname[x],
                                            "quizid": quizlist[x],
                                            "questions": [question_info],  
                                            "used": False
                                        })
                                else:
                                    # If student_id doesn't exist in studentmap, create it with current quiz and question
                                    studentmap[student_id] = [{
                                        "quizname": quizname[x],
                                        "quizid": quizlist[x],
                                        "questions": [question_info], 
                                        "used": False
                                    }]

                # Save to the database
                for key in studentmap.keys():
                    try:
                        collection_name.update_one({'_id': str(key)}, {"$set": {str(courseid): studentmap[key]}}, upsert=True)
                    except Exception as e:
                            print("Error:", e)
    except Exception as e:
        print("Error:", e)
    return 1


def clean_text(text):
    # Normalize and filter to keep only ASCII characters
    return ''.join(char for char in text if ord(char) < 128)


