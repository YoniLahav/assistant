import os
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from config import OPENAI_API_KEY
import json
from datetime import datetime

system_message = SystemMessage(
    f"Today is {datetime.today().strftime('%d-%m-%Y')}. You are an AI personal assistant. You help the USER with general tasks like getting weather data, checking their calendar, etc. You must be formal and polite when addressing the USER. When answering a question, you must give accurate data you obtained from the tools at your disposal; you mustn't make up information yousrself. When listing the USER's events you MUST start with a new line, and list the events off one by one in a numbered list with a new line after each listing. Each event should have a name and a start and end date, and possibly times. When including those parameters, make sure to only print them if they exist! If you don't have the data, simply don't print anything.")

async def init_model():

    print("initializing model")

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    model = init_chat_model("gpt-4o-mini", model_provider="openai", streaming=True)

    # Create client without using context manager
    client = MultiServerMCPClient({
        "calendar": {
            "url": "http://localhost:8000/sse",
            "transport": "sse",
        }
    })

    await client.__aenter__()
    
    # Get tools
    tools = client.get_tools()

    return (model.bind_tools(tools), {tools[i].name: tools[i] for i in range(0, len(tools))}, client)


def send_message(model, tools, request_data):
    messages = [system_message]

    # First, add previous messages
    previous_messages = request_data.get("previousMessages", [])
    for msg in previous_messages:
        role = msg.get("role")
        text = msg.get("text", "")
        if role == "user":
            messages.append(HumanMessage(text))
        elif role == "assistant":
            messages.append(AIMessage(text))
        else:
            raise ValueError(f"Unsupported role: {role}")

    # Add the new incoming message
    new_message = request_data.get("message", {})
    new_role = new_message.get("role")
    new_text = new_message.get("text", "")
    if new_role == "user":
        messages.append(HumanMessage(new_text))
    elif new_role == "assistant":
        messages.append(AIMessage(new_text))
    else:
        raise ValueError(f"Unsupported role: {new_role}")
    
    print("received message: " + new_text)

    return generate_stream(model, tools, messages)


async def generate_stream(model, tools, messages):

    first = True
    gathered = None
    tool_used = False

    async for chunk in model.astream(messages):

        if chunk.content:
            yield json.dumps({"type": "content", "token": chunk.content}) + "\n"

        if first:
            gathered = chunk
            first = False
        else:
            gathered += chunk

    messages.append(gathered)

    if gathered:
        for tool_call in gathered.tool_calls:

            name = tool_call['name']
            args = tool_call['args']
            call_id = tool_call['id']

            tool = tools.get(name)
            
            result = await tool.ainvoke(input=args)

            tool_message = ToolMessage(
                content=str(result),
                tool_call_id=call_id
            )

            messages.append(tool_message)
            tool_used = True

    if tool_used:    
        async for chunk in model.astream(messages):
            if chunk.content:
                yield json.dumps({"type": "content", "token": chunk.content}) + "\n"

