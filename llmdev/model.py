import multiprocessing
import ollama
from flask import Flask, request

app  = Flask(__name__)

def calculate_quare(user_input):
    stream  = ollama.chat(
        model='gemma2:latest',
        messages=[{'role': 'user', 'content': user_input}],
        stream=True,
    )
    answer = ""
    for chunk in stream:
        #print(chunk['message']['content'], end='', flush=True)
        answer += str(chunk['message']['content'])
    return answer

@app.route('/square', methods=['GET'])
def get_square():
    try:
        number  = str(request.args['number'])
        print("API input:", number)
        result  = multiprocessing.Pool().map(calculate_quare, [number])
        return {'result': result[0]}
    except ValueError:
        return {'error': 'Invalid question'}, 400

if __name__ == '__main__':
    app.run(debug=True)

