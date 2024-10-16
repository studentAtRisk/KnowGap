# main.py
# 
# Host an endpoint to generate helpful study materials (youtube review videos) given
# an assignment/quiz/test 
#

import openai
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_query(question):

    prompt = f"""
    Take the following question from a quiz, homework, or exam, and generate an effective YouTube video search query that will help someone find educational videos to study the topic. The search query should:
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

# endpoint
@app.route('/process_quiz', methods=['POST'])
def process_quiz():
    data = request.json

    if not data or 'questions' not in data:
        return jsonify({'error': 'Invalid request, see documentation'}), 400

    questions = data['questions']
    if not isinstance(quiz, list):
        return jsonify({'error': 'Invalid questions format, expected a list of questions'}), 400

    results = []

    for question in quiz:
        search_query = get_youtube_search_query(question['question'])
        results.append({
            'question': question['question'],
            'youtube_query': search_query
        })

    return jsonify({'recommendations': results})


print(generate_query("What happens when you dereference a null pointer?"))
