
#This call questions statistics into flask. It will make a webpage that runs off your ports (1. to practice flask. 2. To show all the info)
from flask import jsonify
import requests
from pymongo import MongoClient
import datetime
from bs4 import BeautifulSoup
import os

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

def get_token_collection():
    client = MongoClient(DB_CONNECTION_STRING)
    database = client['StudentsAtRisk']
    
    return database['Tokens']

def get_database():
 
   client = MongoClient(DB_CONNECTION_STRING)
 
   # create/select the database with inputted name
   return client['Courses']

def updatequizrec(courseid, access_token, dbname, collection_name, currentquiz):



    api_url = f'https://canvas.instructure.com/api/v1/courses/{courseid}/quizzes/{currentquiz}/statistics'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }

    #print("yippoiee")
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            questiontext = []
            selectors = [[]]
            noanswerset = ["multiple_choice_question", "true_false_question", "short_answer_question"]
            answerset = ["fill_in_multiple_blanks_question", "multiple_dropdowns_question", "matching_question"]
            
            #print(selectors[0])
            #print("check this shi out^")
            
            for x in range(len(data["quiz_statistics"][0]["question_statistics"])):
                #take out html text
                questiontext.append(BeautifulSoup(data["quiz_statistics"][0]["question_statistics"][x]["question_text"]).get_text())
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
            print("successfully saved students's quesitons for quiz")
                
            #print(selectors)
            return [questiontext, selectors]

        else:
            print("error")
            return {'error'f'Failed to fetch data from API: {response.text}'}, response.status_code
    except Exception as e:
        print("everyday!"+ str(e))
        return {'error': str(e)}, 500

def updateassignments(courseid, access_token, assignmentmaxscore, dbname, collection_name):


    api_url = f'https://canvas.instructure.com/api/v1/courses/{courseid}/students/submissions?grouped=true&include[]=total_scores&student_ids[]=all&include[]=assignment&rubric_assessment=true'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()



            seen_assignment_ids = set()

            # Filter out duplicates based on `assignment_id`


            print("length of data")
            print(len(data))
            for assignment in data:
                print("how many repeats?")




                print(assignment["submissions"][1])
                data_sorted = sorted(
                                        (submission for submission in assignment["submissions"] if submission['workflow_state'] == "graded"), 
                                        key=lambda x: datetime.datetime.strptime(x['graded_at'], '%Y-%m-%dT%H:%M:%SZ'), 
                                        reverse=True)
                print("its here?")
                rawgrade = []
                rawrecent = []
                unique_data = []
                allgrades = []
                recentgrades = []
                print("oh lah lah")
                for item in data_sorted:
                    print(item)
                    if item['assignment_id'] not in seen_assignment_ids:
                        unique_data.append(item)
                        seen_assignment_ids.add(item['assignment_id'])


                    
                #print(assignmentmaxscore)
                #print("checkpoiunt 0")
                #print(data_sorted[0]["assignment_id"])
                #print(assignmentmaxscore[data_sorted[0]["assignment_id"]])
                    print("check one!")
                for x in range(len(unique_data)):
                    if unique_data[x]["assignment_id"] not in assignmentmaxscore:
                        continue
                    assignmentgrade =  unique_data[x]["entered_score"] / float(assignmentmaxscore[unique_data[x]["assignment_id"]])
                    assignmentgrade = round(assignmentgrade, 2) 
                    print("look here!")
                    print(unique_data[x])
                    assignmentname = unique_data[x]["assignment"]["name"]

                    allgrades.append({"name":assignmentname, "grade":assignmentgrade})
                    rawgrade.append(assignmentgrade)

                    if len(allgrades) > 5:
                        recentgrades = allgrades[:5]
                    else:
                        recentgrades = allgrades

                    if len(rawgrade) > 5:
                       rawrecent = rawgrade[:5]
                    else:
                       rawrecent = rawgrade


                    print("THE VERY END?")
                    print(allgrades)


                print("hey whats this")
                print(assignment["user_id"])
                print(allgrades)
                print(recentgrades)
                
                try:
                    collection_name.update_one({'_id': str(assignment["user_id"])}, {"$set": {"assignment_scores": allgrades, "recent_scores": recentgrades, "raw_grades": rawgrade, "raw_recent":rawrecent}}, upsert=True)

                except Exception as e:
                    print("Error:", e)

            print("successfully saved students's assignment grades")
                

            return len(data) #["quiz_statistics"][0]["question_statistics"]
        else:
            return {'error': f'Failed to fetch data from API: {response.text}'}, response.status_code

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500



def getquizzes(courseid, access_token):


    api_url = f'https://canvas.instructure.com/api/v1/courses/{courseid}/quizzes'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            quizlist = []
            quizname = []
            for x in range(len(data)):
                quizlist.append(data[x]["id"])
                quizname.append(data[x]["title"])
            return quizlist, quizname 
        else:
            return {'error': f'Failed to fetch data from API: {response.text}'}, response.status_code
    except Exception as e:
        return {'error': str(e)}, 500

def getassignments(courseid, access_token):


    api_url = f'https://canvas.instructure.com/api/v1/courses/{courseid}/assignments'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            thisdict = {}
            for x in range(len(data)):
                thisdict.update({data[x]["id"]: data[x]["points_possible"]})
            return thisdict 
        else:
            return {'error': f'Failed to fetch data from API: {response.text}'}, response.status_code
    except Exception as e:
        return {'error': str(e)}, 500
    
#it starts here
def updatedb(courseid, access_token):

    # Selects newly created databse
    #print("connecting...")
    dbname = get_database()
    # Makes collection with inputted name
    collection_name = dbname[str(courseid)]
    #print("connection complete")

    quizlist, quizname = getquizzes(courseid,access_token)
    assignmentmaxscore = getassignments(courseid, access_token)
    api_url = f'https://canvas.instructure.com/api/v1/courses/{courseid}/enrollments'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            studentmap = {}


            #updateassignments(courseid, access_token, assignmentmaxscore, dbname, collection_name)
            for x in range(len(data)):
                
                if(data[x]["type"] == "StudentEnrollment"):


                    try:
                        collection_name.update_one({'_id': str(data[x]["user_id"])}, {"$set": {"current_grade": data[x]["grades"]["current_score"]}}, upsert=True)
                        
                    except Exception as e:
                        print("Error:", e)
                    print("successfully saved "+data[x]["user"]["name"]+"'s final grade")

            #update quiz topics
            for x in range(len(quizlist)):
                results = updatequizrec(courseid, access_token, dbname, collection_name, quizlist[x])

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
                                        quiz['questions'].append(question)
                                        quiz_found = True
                                        break

                                # if the quiz doesn't exist, add a new entry for this quiz
                                if not quiz_found:
                                    studentmap[student_id].append({
                                        "quizname": quizname[x],
                                        "questions": [question],
                                        "used": False
                                    })
                            else:
                                # if student_id doesn't exist in studentmap, create it with current quiz and question
                                studentmap[student_id] = [{
                                    "quizname": quizname[x],
                                    "questions": [question],
                                    "used": False
                                }]

            # save to the database
            for key in studentmap.keys():
                try:
                    collection_name.update_one({'_id': str(key)}, {"$set": {"failed_questions": studentmap[key]}}, upsert=True)
                except Exception as e:
                    print("Error:", e)
    except Exception as e:
        print("Error:", e)
    return 1





