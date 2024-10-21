
from flask import jsonify
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from pandas import DataFrame
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import asyncio
import aiohttp

global_amtofquizzes =  5

async def get_database(connectionString):
 
   # Connection to database string. Change this to switch databases
   CONNECTION_STRING = connectionString

   client = AsyncIOMotorClient(CONNECTION_STRING)
 
   # Create/select the database with inputted name
   return client['KnowGap']

async def update_quiz_rec(courseid, access_token, dbname, collection_name, currentquiz, link):



    api_url = f'https://{link}/api/v1/courses/{courseid}/quizzes/{currentquiz}/questions'
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

                    

                    
                    for x in range(len(data)):
                        questiontext.append(BeautifulSoup(data[x]["question_text"], features="html.parser").get_text())
                        questiontext[x] = clean_text(questiontext[x])   
                        questionid.append(data[x]["id"])
                        

                    return questiontext, questionid

                else:
                    print("error" )
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
                    unfiltered_data = await response.json()
                    max_date = datetime.now(timezone.utc)
                    # Sorts data by most recent unlocked quiz that is published to oldest

                    data = sorted(
                        [
                            item for item in unfiltered_data
                            if item["published"] and item["all_dates"][0]["unlock_at"] and parse_date(item["all_dates"][0]["unlock_at"]) <= max_date
                        ],
                        key=lambda x: (
                            # Sort by unlock date in descending order (later dates first)
                            parse_date(x["all_dates"][0]["unlock_at"])
                        ),
                        reverse=True  # Sorting in descending order to get later dates first
                    )

                    
                    
                    quizlist = []
                    quizname = []
                    
                    for x in range(min(len(data), global_amtofquizzes)):
                        quizlist.append(data[x]["id"])
                        quizname.append(data[x]["title"])

                    print(quizname)
                    return quizlist, quizname 
                else:
                    print("did we error here?")
                    return {'error': f'Failed to fetch data from API: {response.text}'}, response.status
    except Exception as e:
        print(e)
        return {'error' : str(e)}, 500


    
#it starts here
async def update_db(courseid, access_token, connectionString, link):

    # Selects newly created databse

    dbname = await get_database(connectionString)
    # Makes collection with inputted name
    collection_name = dbname["Quiz Questions"]


    quizlist, quizname = await get_quizzes(courseid,access_token, link)
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


                    course_name = await get_course_details(courseid, access_token, link)
                    
                    
                    for x in range(len(quizlist)):
 
                        questiontext, questionid = await update_quiz_rec(courseid, access_token, dbname, collection_name, quizlist[x], link)

                        # Finally, save to the database.
                        for y in range(len(questiontext)):
                            try:
                                print(quizlist[x])
                                print(questionid[y])
                                collection_name.update_one({'quizid': quizlist[x],  'courseid': str(courseid), "course_name": course_name, "questionid": str(questionid[y])}, {"$set": {"question_text": questiontext[y]}},upsert=True)
                            except Exception as e:
                                print("Error:", e)
    except Exception as e:
        print("Error:", e)
    return 1


async def get_course_details(courseid, access_token, link):


    api_url = f'https://{link}/api/v1/courses/{courseid}'
    headers ={
        'Authorization': f'Bearer {access_token}'
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    course_details = await response.json()
                    course_name = course_details.get("name", "Course name not found")
                    return course_name
                else:
                    print(f"Failed to retrieve course. Status code: {response.status_code}")
    except Exception as e:
        return {'error': str(e)}, 500




def parse_date(date_str):
    
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.astimezone(timezone.utc)  # Normalize to UTC
    return None

max_date = datetime.now(timezone.utc)  # Ensure max_date is in UTC

def clean_text(text):
    # Normalize and filter to keep only ASCII characters
    return ''.join(char for char in text if ord(char) < 128)


courseid = "10496683"  # Example course ID
access_token = "7~WvADyKw8mGWm4DUk4rWvWPVw2Kr3BXwtH4GNffABcxMHRR2KTraCfc2FB2Qf6zFw"  # Example API token
connectionString = "mongodb+srv://jordan917222:PPJjEItclZaEECv7@studentsatrisk.ptqdmcu.mongodb.net/" # MongoDB connection string
link = "canvas.instructure.com" # Mock URL to Canvas API

# Run the main async function
asyncio.run(update_db(courseid, access_token, connectionString, link))

