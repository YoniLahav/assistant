from quart import Quart, request, Response
from assistant import send_message, init_model
from calendar_service import get_events
# import asyncio

app = Quart(__name__)

@app.before_serving
async def startup():
    app.model, app.tools, app.mcp_client = await init_model()


@app.route('/', methods=['GET'])
def home():
    return "Hello, Flask!"

@app.route('/events', methods=['GET'])
def events():

    get_events('2025-04-01', '2025-04-30')
    return "Events Gathered"

@app.route('/chat', methods=['POST'])
async def chat():
    data = await request.get_json()
    return Response(send_message(app.model, app.tools, data), mimetype='application/x-ndjson')

# @app.after_serving
# async def shutdown():
#     #await app.mcp_client.__aexit__(None, None, None)

if __name__ == "__main__":
    app.run(debug=True)
