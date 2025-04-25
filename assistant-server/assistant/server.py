from flask import Flask, request, Response, stream_with_context
from assistant import send_message

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Hello, Flask!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    return Response(stream_with_context(send_message(data)), mimetype='application/x-ndjson')

if __name__ == "__main__":
    app.run(debug=True)
