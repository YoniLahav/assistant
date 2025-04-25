import os

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from config import OPENAI_API_KEY
import json

# # Start the chat loop
# print("Chatbot is ready! Type 'exit' to quit.")
# while True:
#     user_input = input("You: ")
#     if user_input.lower() in ['exit', 'quit']:
#         print("Assistant: Goodbye!")
#         break

#     messages.append(HumanMessage(user_input))

#     print("Assistant: ", end="")

    # for token in model.stream(messages):
    #    print(token.content, end="")
    
#     print()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

model = init_chat_model("gpt-4o-mini", model_provider="openai", streaming=True)
system_message = SystemMessage("You are an AI personal assistant. You help the USER with general tasks like getting weather data, checking their calendar, etc. You must be formal and polite when addressing the USER.") # When answering a question, you must give accurate data you obtained from the tools at your disposal; you mustn't make up fabricated informatino yousrself.messages = [system_message, HumanMessage("Hey, how are you?")]

def generate_stream(message_list):
    for chunk in model.stream(message_list):
        if chunk.content:
            data = {"token": chunk.content}
            yield json.dumps(data) + "\n"


def send_message(request_data):
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

    return generate_stream(messages)