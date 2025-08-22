import os
import json
from my_config import config
import chainlit as cl
from dotenv import load_dotenv
import requests
from agents import Agent, Runner, function_tool

# --- Step 1: Load .env variables ---
load_dotenv()
ALTRAMSG_TOKEN = os.getenv("ALTRAMSG_TOKEN")
ALTRAMSG_INSTANCE_ID = os.getenv("ALTRAMSG_INSTANCE_ID")

# --- Step 2: Load contacts.json ---
with open("contacts.json", "r", encoding="utf-8") as f:
    CONTACTS = json.load(f)

# --- Step 3: Define tool for UltraMsg API ---
@function_tool
def send_ultramsg(token: str, instance_id: str, name: str, body: str) -> str:
    """
    Send a WhatsApp message using UltraMsg API.
    The recipient is identified by their NAME from contacts.json.
    """
    if name not in CONTACTS:
        return f"❌ Contact '{name}' not found in contacts.json."

    to = CONTACTS[name]

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    payload = {
        "token": token,
        "to": to,
        "body": body
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    return response.text

# --- Step 4: Create Agent ---
agent = Agent(
    name="WhatsAppSender",
    instructions=(
        "You are a helpful WhatsApp messaging agent. "
        "When asked to send a message, extract the NAME and BODY, "
        "look up the number in contacts.json, then call the send_ultramsg tool."
    ),
    tools=[send_ultramsg],
)

# --- Step 5: Chainlit UI ---
@cl.on_chat_start
async def start():
    await cl.Message(content="# 📱 Personal WhatsApp Agent\n\nType your request like:\n`Send message 'Hello' to Ahsen`").send()

@cl.on_message
async def main(message: cl.Message):
    # Run agent with user input
    result = Runner.run_sync(
        agent,
        f"{message.content} using token {ALTRAMSG_TOKEN} and instance {ALTRAMSG_INSTANCE_ID}",
        run_config=config
    )

    # Show agent output in Chainlit UI
    # uv run chainlit run main.py



  
    await cl.Message(content=f"✅ Agent Output:\n{result.final_output}").send()
