#This call questions statistics into flask. It will make a webpage that runs off your ports (1. to practice flask. 2. To show all the info)
from flask import jsonify
import requests
from pymongo import MongoClient
from pandas import DataFrame
import datetime
from bs4 import BeautifulSoup
import asyncio
import aiohttp


async def get_database(connectionString):
 
   # connection to database string. Change this to switch databases
   CONNECTION_STRING = connectionString

   client = MongoClient(CONNECTION_STRING)
 
   # create/select the database with inputted name
   return client['Courses']

async def updatequizrec(courseid, access_token, dbname, collection_name, currentquiz, link):



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
                    selectors = [[]]
                    noanswerset = ["multiple_choice_question", "true_false_question", "short_answer_question"]
                    answerset = ["fill_in_multiple_blanks_question", "multiple_dropdowns_question", "matching_question"]
                    
                    #print(selectors[0])
                    #print("check this shi out^")
                    
                    for x in range(len(data["quiz_statistics"][0]["question_statistics"])):
                        #take out html text. feature gets rid of print warning
                        questiontext.append(BeautifulSoup(data["quiz_statistics"][0]["question_statistics"][x]["question_text"], features="html.parser").get_text())
                        selectors.append([])
                        if data["quiz_statistics"][0]["question_statistics"][x]["question_type"] in noanswerset:
                            for y in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answers"])):
                                #print("what do we have here...")
                                #print(data["quiz_statistics"][0]["question_statistics"][x]["answers"][y])
                                if(data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["correct"] == False):
                                    if(len(data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["user_ids"]) > 0):
                                        #print("my number is "+str(x))
                                        selectors[x] += data["quiz_statistics"][0]["question_statistics"][x]["answers"][y]["user_ids"]
                                    else:
                                        selectors[x] += [-1]
                        if data["quiz_statistics"][0]["question_statistics"][x]["question_type"] in answerset:
                            for z in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"])):
                                for y in range(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"])):
                                    #print("what do we have here...")
                                    #print(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y])
                                    if(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["correct"] == False):
                                        if(len(data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["user_ids"]) > 0):
                                            #print("my number is "+str(x))
                                            selectors[x] += data["quiz_statistics"][0]["question_statistics"][x]["answer_sets"][z]["answers"][y]["user_ids"]
                                        else:
                                            selectors[x] += [-1]                
                    #print("successfully saved students's quesitons for quiz")
                        
                    #print(selectors)
                    return [questiontext, selectors]

                else:
                    print("error")
                    return {'error'f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        return {'error : Failed to grab quiz statistics due to': str(e)}, 500


async def getquizzes(courseid, access_token, link):


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
                    for x in range(len(data)):
                        quizlist.append(data[x]["id"])
                        quizname.append(data[x]["title"])
                    print("DONE!")
                    return quizlist, quizname 
                else:
                    return {'error': f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        return {'error': str(e)}, 500


    
#it starts here
async def updatedb(courseid, access_token, connectionString, link):

    # Selects newly created databse
    #print("connecting...")
    dbname = await get_database(connectionString)
    # Makes collection with inputted name
    collection_name = dbname[str(courseid)]
    #print("connection complete")

    quizlist, quizname = await getquizzes(courseid,access_token, link)
    print(quizlist)
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



                    #update quiz topics
                    print("trust the process")
                    for x in range(len(quizlist)):
                        results = await updatequizrec(courseid, access_token, dbname, collection_name, quizlist[x], link)
                        for y in range(len(results[1])):

                            for z in range(len(results[1][y])):
                                if results[1][y][z] != -1:
                                    student_id = results[1][y][z]
                                    question = results[0][y]

                                    # if student already has an entry in studentmap
                                    if student_id in studentmap:
                                        # check if current quizname[x] already exists in the student's failed_questions list
                                        quiz_found = False
                                        for quiz in studentmap[student_id]:
                                            if quiz['quizname'] == quizname[x]:
                                                quiz['questions'].add(question)
                                                quiz_found = True
                                                break

                                        # if the quiz doesn't exist, add a new entry for this quiz
                                        if not quiz_found:
                                            studentmap[student_id].append({
                                                "quizname": quizname[x],
                                                "questions": {question},
                                                "used": False
                                            })
                                    else:
                                        # if student_id doesn't exist in studentmap, create it with current quiz and question
                                        studentmap[student_id] = [{
                                            "quizname": quizname[x],
                                            "questions": {question},
                                            "used": False
                                        }]

                    # save to the database
                    for key in studentmap.keys():
                        
                        for quiz in studentmap[key]:
                            quiz['questions'] = list(quiz['questions']) 
                        try:
                            collection_name.update_one({'_id': str(key)}, {"$set": {"failed_questions": studentmap[key]}}, upsert=True)
                        except Exception as e:
                            print("Error:", e)
    except Exception as e:
        print("Error:", e)
    return 1

# testing purposes
# async def main():
#     courseid = 123
#     access_token = '123'
#     connectionString = "123"
#     link = 'website link'
#     await updatedb(courseid, access_token, connectionString, link)
#     print("Updated student assessment for this course")

# if __name__ == "__main__":
#     asyncio.run(main())
