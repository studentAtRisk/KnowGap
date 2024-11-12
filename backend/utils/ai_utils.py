# Import necessary libraries
import asyncio
from openai import AsyncOpenAI
from config import Config
# Initialize OpenAI client with your API key
client = AsyncOpenAI(api_key=Config.OPENAI_KEY)

# Define the coroutine for generating core topic with GPT
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
    # Set up the prompt
    prompt = (
        f"Based on the following question from course {course_name}, "
        f"generate a concise, specific core topic that is relevant to the subject matter. "
        f"You can assume the course is at a college/university level."
        f"The topic should be no longer than 4-5 words and should directly relate to the main concepts: {question_text}"
    )

    # Append course context if available
    if course_context:
        prompt += f"\nHere's what the instructor gave us, so use it to generate a more relevant topic in the context of the course itself: {course_context}"

    # Prepare message for chat model
    messages = [{"role": "user", "content": prompt}]

    try:
        # Make the async call to GPT using the client
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=50,
            top_p=0.5
        )
        
        # Extract and clean up the generated topic
        core_topic = response.choices[0].message.content.strip().strip('"').strip("'")
        return {"success": True, "core_topic": core_topic}

    except Exception as e:
        print(f"Error generating core topic: {e}")
        return {"success": False, "error": str(e)}

# Main block to test the function
if __name__ == "__main__":
    # Define a sample question and course details
    question_text = "Explain the process of photosynthesis in plants."
    course_name = "Biology 101"
    course_context = "Focus on energy conversion in plant cells."

    # Run the test
    async def test_generate_core_topic():
        result = await generate_core_topic(question_text, course_name, course_context)
        if result["success"]:
            print(f"Generated core topic: {result['core_topic']}")
        else:
            print(f"Error: {result['error']}")

    # Execute the test coroutine
    asyncio.run(test_generate_core_topic())
