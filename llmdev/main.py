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

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

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

if __name__ == "__main__":
    path = "/home/dsantamaria/ucf/UCF-Student-Risk-Predictor/querygen/data/stats/exams/exam1.json"
    quiz_data = load_quiz_from_file(path)
    if quiz_data:
        results = process_quiz(quiz_data)
        for result in results:
            print(f"Question: {result['question']}")
            print(f"Suggested YouTube query: {result['youtube_query']}\n")
