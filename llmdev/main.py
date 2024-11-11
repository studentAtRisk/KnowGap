# main.py
# 
# Host an endpoint to generate helpful study materials (youtube review videos) given
# an assignment/quiz/test 
#

import json
import openai
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from ytsearch import query_videos
from youtube_transcript_api import YouTubeTranscriptApi
from engagement import YTEngagementUtility
from pytube import extract
from ytstats import YTStatsUtility
from youtubesearchpython import VideosSearch

load_dotenv()
app = Flask(__name__)
youtube_api_key = "AIzaSyB71CG_xbctso7Q7c_cRBfJJV1w5QHH-Y8"
openai.api_key = os.getenv('OPENAI_API_KEY')

def askgpt(prompt, model="gpt-4o"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )

        search_query = response.choices[0].message.content

        return search_query
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error generating query"

def generate_query(question):

    prompt = f"""
    Take the following question and generate an effective YouTube video search query that will help someone find educational videos to study the topic. The search query should:
    Be concise and include the most relevant keywords and phrases from the question.
    Optimize for YouTube's search algorithm by considering common video titles and descriptions.
    Avoid unnecessary words or details that don't aid in finding helpful videos.
    Avoid formatting, quotes, or otherwise modifying the query. Only return the words in the query.
    Consider the context that this question might appear in, such as which part of a course or series
    and use that to help generate the query, if it is helpful.
    {question}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )

        search_query = response.choices[0].message.content

        return search_query
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Error generating query"

def get_common_wrong_answers(quiz):
    return gpt("hello!")

def process_quiz(quiz_data):
    if 'questions' not in quiz_data:
        print("Invalid quiz data: 'questions' key not found.")
        return

    questions = quiz_data['questions']
    results = []

    for question in questions:
        question_text = question['question']
        search_query = generate_query(question_text)  # Call the generate_query function
        results.append({
            'question': question_text,
            'youtube_query': search_query
        })

    return results

def get_transcript(youtube_url):
    stats_util = YTStatsUtility(youtube_api_key)
    video_id = stats_util.get_video_id(youtube_url)
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try fetching the manual transcript
    try:
        transcript = transcript_list.find_manually_created_transcript()
        language_code = transcript.language_code  # Save the detected language
    except:
        # If no manual transcript is found, try fetching an auto-generated transcript in a supported language
        try:
            generated_transcripts = [trans for trans in transcript_list if trans.is_generated]
            transcript = generated_transcripts[0]
            language_code = transcript.language_code  # Save the detected language
        except:
            # If no auto-generated transcript is found, raise an exception
            raise Exception("No suitable transcript found.")

    full_transcript = " ".join([part['text'] for part in transcript.fetch()])
    return full_transcript, language_code  # Return both the transcript and detected language


def load_quiz_from_file(file_path):
    """Loads the quiz data from a given JSON file path."""
    try:
        with open(file_path, 'r') as file:
            quiz_data = json.load(file)
            return quiz_data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return None

def find_question_in_transcript(question, transcript):
    prompt = f"""
    You are an expert analyst. Your goal is to determine whether the following exam question, or any variant of it, was addressed in the provided YouTube video transcript.

    Instructions:

    Read Carefully: Thoroughly read the exam question and the video transcript.

    Identify Key Concepts: Extract the main ideas, keywords, and concepts from the exam question.

    Analyze the Transcript: Search for these concepts or any related topics within the transcript.

    Compare and Contrast: Evaluate the similarities and differences between the exam question and the content of the transcript.

    Conclude: State clearly whether a variant of the exam question was covered in the video, based on your analysis.

    Exam Question:

    ```
    {question}
    ``` 

    YouTube Video Transcript:

    ```
    {transcript}
    ``` 

    Your Response Should Include:

    A yes or no answer to whether the transcript includes either an answer to the exam question, or references something similar
    to the question given.
    Be structured and concise.
    Give your response in a json with "answer" field only.
    Do not include unneccessary text and do not include a ```json ``` markdown formatter.
    Only the json object with the field, and a yes or no vaule.
    """
    
    response = askgpt(prompt, "gpt-3.5-turbo")
    return response

def get_quiz_from_path(path):
    return load_quiz_from_file(path)

def foreach_question(quiz_data, func):
    quiz_json = process_quiz(quiz_data)
    ret = []
    for data in quiz_json :
        ret.append(func(data['question']))
    print(ret)
    return ret

def generate_accuracy_arr(quiz_data, youtube_link):
    transcript = get_transcript(youtube_link)
    ret = []
    for data in quiz_data['questions']:
        ret.append(find_question_in_transcript(data['question'], transcript))
    return ret

def find_accuracy(arr):
    sum = 0
    for i in arr:
        j = json.loads(i)
        sum += j['answer'].lower() == "yes"
    print(f"Found {sum} potential answers out of {len(arr)} questions")
    print(f"Accuracy: {sum / len(arr)}")
    return sum / len(arr)

def get_relevancy(quiz, transcript):
    return None

def get_engagement(youtube_link):
    engagement_util = YTEngagementUtility(upper_bound=20, lower_bound=0, min_score=0, max_score=25)
    stats_util = YTStatsUtility(youtube_api_key)
    stats = stats_util.get_video_statistics(youtube_link)
    views = int(stats['viewCount'])
    likes = int(stats['likeCount'])
    comments = int(stats['commentCount'])
    return engagement_util.find_engagement(likes, comments, views)

def search_for_videos(query, num_results=1):
    search = VideosSearch(query, limit=num_results)
    results = search.result()['result']
    links = []
    for video in results:
        links.append(video['link'])
    return links

def rank_videos(quiz_data, video_links):
    ranked_videos = []

    for link in video_links:
        try:
            transcript = get_transcript(link)
            accuracy_arr = generate_accuracy_arr(quiz_data, link)
            accuracy = find_accuracy(accuracy_arr)

            engagement = get_engagement(link)

            ranking = 0.5 * accuracy + 0.5 * engagement

            print(f"Link: {link}, Accuracy: {accuracy}, Engagement: {engagement}, Total Ranking: {ranking}")

            ranked_videos.append({
                'link': link,
                'ranking': ranking
            })
        except Exception as e:
            print(f"Error processing video {link}: {e}")

    ranked_videos.sort(key=lambda x: x['ranking'], reverse=True)
    return ranked_videos


if __name__ == "__main__":
    path = "/home/dsantamaria/ucf/UCF-Student-Risk-Predictor/querygen/data/stats/exams/exam1.json"
    quiz_data = load_quiz_from_file(path)

    if quiz_data:
        results = process_quiz(quiz_data)
        queries = [result['youtube_query'] for result in results]

        video_links = []
        for query in queries:
            search_results = search_for_videos(query, 1)
            if search_results:
                video_links.extend(search_results)

        print("Videos fetched: ", video_links)

        ranked_videos = rank_videos(quiz_data, video_links)

        for video in ranked_videos:
            print(f"Link: {video['link']}, Ranking: {video['ranking']}")
    else:
        print("No quiz data found!")
