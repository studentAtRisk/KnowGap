import openai
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from ytsearch import query_videos

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

def query_gpt(question):

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


def parse_exam_file(file_path):
    questions = []
    current_question = []
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and line[0].isdigit() and line[1] == '.':
                if current_question:
                    questions.append(' '.join(current_question).strip())
                    current_question = []
            current_question.append(line)

        if current_question:
            questions.append(' '.join(current_question).strip())

    return questions

def process_exams(model, exam_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    exam_files = [f for f in os.listdir(exam_directory) if f.startswith("exam") and f.endswith(".txt")]

    for exam_file in exam_files:
        exam_path = os.path.join(exam_directory, exam_file)
        output_path = os.path.join(output_directory, f"output_{exam_file}")
        
        questions = parse_exam_file(exam_path)
        
        with open(output_path, 'w') as output_file:
            for question in questions:
                prompt = f"""
                I will provide a question, and I need you to return only the general topic or subject in the form of a search query. 
                Output should be a simple phrase with no additional text, no emojis, no explanations, and no formatting. Strictly return the topic as a search query.

                Now, analyze this question and return only the search query:

                {question}
                """
                query_result = query_ollama(model, prompt)
                
                output_file.write(f"Question: {question}\n")
                output_file.write(f"Search Query: {query_result}\n\n")

        print(f"Processed {exam_file} and wrote output to {output_path}")

if __name__ == "__main__":
    exam_directory = "data/bio/exams/"
    output_directory = "data/bio/output/"
    
    process_exams(model='gemma2:latest', exam_directory=exam_directory, output_directory=output_directory)
