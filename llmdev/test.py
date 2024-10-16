import os
import ollama

def query_ollama(model, prompt):
    stream = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )
    answer = ""
    for chunk in stream:
        answer += str(chunk['message']['content'])
    return answer.strip()

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
