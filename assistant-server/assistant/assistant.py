import os
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from config import OPENAI_API_KEY
import json
from collections import defaultdict
import traceback
from anyio import ClosedResourceError

system_message = SystemMessage("You are an AI personal assistant. You help the USER with general tasks like getting weather data, checking their calendar, etc. You must be formal and polite when addressing the USER.") # When answering a question, you must give accurate data you obtained from the tools at your disposal; you mustn't make up fabricated informatino yousrself.messages = [system_message, HumanMessage("Hey, how are you?")]

async def init_model():

    print("initializing model")

    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    model = init_chat_model("gpt-4o-mini", model_provider="openai", streaming=True)

    # Create client without using context manager
    client = MultiServerMCPClient({
        "math": {
            "url": "http://localhost:8000/sse",
            "transport": "sse",
        }
    })
    
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


async def generate_stream(model, tools, message_list):
    tool_call_accumulators = defaultdict(lambda: {"name": None, "args": ""})
    tool_call_ids = {}

    async for chunk in model.astream(message_list):

        if chunk.content:
            yield json.dumps({"type": "content", "token": chunk.content}) + "\n"

        if hasattr(chunk, 'tool_call_chunks'):
            for tc in chunk.tool_call_chunks:

                idx = tc['index']

                if tc['name']:
                    tool_call_accumulators[idx]["name"] = tc['name']
                if tc['args']:
                    tool_call_accumulators[idx]["args"] += tc['args']
                if tc['id']:
                    tool_call_ids[idx] = tc['id']

        # Check if any tool calls are complete
        for idx, acc in list(tool_call_accumulators.items()):
            name = acc["name"]
            args_str = acc["args"]
            if name and args_str:
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    continue  # Wait for more chunks to complete the JSON

                print(f"received valid args for tool_call: {args}")
                print(f"getting tool by name: {name} from tools: {tools}")

                # Execute the tool
                tool = tools.get(name)
                if tool:
                    print("running tool:")
                    
                    try:
                        result = await tool.ainvoke(input=args)
                    except ClosedResourceError as e:
                            print("Encountered ClosedResourceError: The resource was closed before the operation could complete.")
                            traceback.print_exc()
                            result = None
                    except Exception as e:
                        print(f"Error invoking tool: {e}")
                        print(f"Exception type: {type(e)}")
                        print(f"Exception repr: {repr(e)}")
                        traceback.print_exc()
                        result = None

                    data = {"tool_result": result}
                    yield json.dumps(data) + "\n"

                    # Create a ToolMessage to inform the model of the tool's result
                    tool_message = ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_ids.get(idx, f"call_{idx}")
                    )
                    message_list.append(tool_message)

                    # Clear the accumulator for this tool call
                    del tool_call_accumulators[idx]
                    del tool_call_ids[idx]
