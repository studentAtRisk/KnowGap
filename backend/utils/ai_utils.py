# utils/ai_utils.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from config import Config

client = OpenAI(api_key=Config.OPENAI_KEY)

async def generate_core_topic(question_text, course_name, course_context=""):
    """
    Generate a concise core topic using GPT for a given question.
    
    Parameters:
    - question_text (str): The text of the question.
    - course_name (str): The name of the course the question belongs to.
    - course_context (str): Additional context for the course, provided by the instructor.

    Returns:
    - str: A concise topic title relevant to the question and course.
    """
    prompt = (
        f"Based on the following question from course {course_name}, "
        f"generate a concise, specific core topic that is relevant to the subject matter. You can assume the course is college/university level"
        f"The topic should be no longer than 4-5 words and should directly relate to the main concepts: {question_text}"
    )
    
    if course_context:
        prompt += f"\nHere's what the instructor gave us, so use it to generate a more relevant topic in the context of the course itself: {course_context}"

    try:
        response = await OpenAI.ChatCompletion.acreate(
            prompt=prompt,
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo-instruct",
            max_tokens=50,
            top_p=0.5,
            temperature=0.7
        )

        # Extracting and cleaning up the generated topic
        core_topic =  response.choices[0].message['content'].strip().strip('"').strip("'")
        return core_topic

    except Exception as e:
        print(f"Error generating core topic: {e}")
        return "Error generating topic"
