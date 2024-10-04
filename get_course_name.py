import requests

# Define your API token and course ID
access_token = "1158~VHXhYzhDTYvthzzarE7ctWCXTBUvEPPnEkkFNxMQF7aGr7vfy8eWfuX63mfQNTuu"
course_id = "1425706"
base_url = "https://webcourses.ucf.edu"

# Set up headers with your access token
headers = {
    "Authorization": f"Bearer {access_token}"
}

# Make the GET request to retrieve the course details
response = requests.get(f"{base_url}/api/v1/courses/{course_id}", headers=headers)

# Check if the request was successful
if response.status_code == 200:
    course_details = response.json()
    course_name = course_details.get("name", "Course name not found")
    print(str(course_details))
    print(f"Course Name: {course_name}")
else:
    print(f"Failed to retrieve course. Status code: {response.status_code}")
