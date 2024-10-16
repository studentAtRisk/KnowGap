import ollama
import sys

def query_ollama(model, prompt):
    stream = ollama.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        stream=True,
    )
    answer = ""
    for chunk in stream:
        answer += str(chunk['message']['content'])
    return answer

def analyze_problem(model, question):
    prompt_text = f"""
    Analyze the following question and determine the general subject or topic:

    {question}
    """
    return query_ollama(model, prompt_text)

def generate_hint(model, question, previous_hints):
    previous_hints_text = "\n".join([f"- {hint}" for hint in previous_hints])
    
    prompt_text = f"""
    The following are hints generated from previous questions:
    {previous_hints_text}

    Now analyze the current question, and provide the topic or subject, while considering prior hints but prioritizing the current question:

    {question}
    """
    return query_ollama(model, prompt_text)

def main(model='gemma2:latest'):
    previous_hints = []

    while True:
        print(">")
        sys.stdout.flush()
        
        question_text = sys.stdin.readline().strip()
        
        hint = analyze_problem(model, question_text)
        print(f"Hint for current question: {hint.strip()}")

        new_hint = generate_hint(model, question_text, previous_hints)
        print(f"Refined hint: {new_hint.strip()}")
        
        previous_hints.append(new_hint.strip())
    
    print("All hints: {")
    for idx, hint in enumerate(previous_hints):
        print(f"({hint}), ", end=" ")
    print("}")

if __name__ == "__main__":
    main()

