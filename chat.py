from flask import Flask, render_template, request, jsonify
import time
import openai
from openai import OpenAI


app = Flask(__name__)

# Global variable to store the thread ID
thread_id = None

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    global thread_id
    msg = request.form["msg"]
    input_text = msg

    # Call the OpenAI API to get the chat response
    response = get_chat_response(input_text)

    return response

def get_chat_response(text):
    global thread_id
    ASSISTANT_ID = "asst_WqR8LoxNDrva7EAX8xXl8WE4"
    client = OpenAI()

    # Create an initial thread if thread_id is None
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id

    user_input = text

    if user_input.lower() == "exit":
        # Reset the thread_id to None when "exit" is received
        thread_id = None
        return "Conversation ended."

    # Add the user's input as a new message to the existing thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)
    print(f"Run Created: {run.id}")

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f" Run Status: {run.status}")
        time.sleep(0.3)

    print("Run Completed!")
    message_response = client.beta.threads.messages.list(thread_id=thread_id)
    messages = message_response.data
    latest_message = messages[0]  # Get the last message
    response = latest_message.content[0].text.value

    return response

if __name__ == '__main__':
    app.run()