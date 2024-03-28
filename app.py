from flask import Flask, request, session
from twilio.rest import Client
import asyncio
from rasa.core.agent import Agent
from rasa.shared.utils.io import json_to_string
import os
import pandas as pd
import time

model1_path = "models/nlu-20240326-232920-purple-compete.tar.gz"
model2_path = "models/nlu-20240327-191236-icy-aside.tar.gz"
CONF_THRESH = 0.5

greetings = ['hello', 'sasa', 'habari', 'aloha', 'jambo', 'uko', 'aje', 'habari yako', 'hi', 'hey', 'help', 'how are you', 'uko fiti', 'uko poa', 'habari ya asubuhi', 'good morning', 'morning', 'good evening', 'good afternoon']

bot_response = pd.read_csv("data/bot_response.csv")
interest = pd.read_csv("data/interest_details.csv")
incidents = pd.read_csv("data/incident_guides.csv")
misinformation = pd.read_csv("data/misinformation_guides.csv")

introduction = bot_response[bot_response['response_type'] == "introduction"].values[0][2:]

main_menu = bot_response[bot_response['response_type'] == "main_menu"].values[0][2:]

download_app_confirm = bot_response[bot_response['response_type'] == "download_app_confirm"].values[0][2:]

anything_else_dialog = bot_response[bot_response['response_type'] == "anything_else_dialog"].values[0][2:]

incident_confirm = bot_response[bot_response['response_type'] == "incident_confirm"].values[0][2:]

app_steps = bot_response[bot_response['response_type'] == "app_steps"].values[0][2:]

download_app_steps = bot_response[bot_response['response_type'] == "download_app_steps"].values[0][2:]

misinformation_confirm = bot_response[bot_response['response_type'] == "misinformation_confirm"].values[0][2:]

counter_misinformation_guide = bot_response[bot_response['response_type'] == "counter_misinformation_guide"].values[0][2:]

misinformation_details_dialog = bot_response[bot_response['response_type'] == "misinformation_details_dialog"].values[0][2:]

locations_list = bot_response[bot_response['response_type'] == "locations_list"].values[0][2:]

interest_list = bot_response[bot_response['response_type'] == "interest_list"].values[0][2:]

interest_details = {k:interest[interest['response_type'] == k].values[0][2:] for k in interest['response_type']}

goodbye = bot_response[bot_response['response_type'] == "goodbye"].values[0][2:]

incident_guides = {k:incidents[incidents['response_type'] == k].values[0][2:] for k in incidents['response_type']}

misinformation_guides = {k:misinformation[misinformation['response_type'] == k].values[0][2:] for k in misinformation['response_type']}

general_misinformation = bot_response[bot_response['response_type'] == "general_misinformation"].values[0][2:]

location_welcome = bot_response[bot_response['response_type'] == "location_welcome"].values[0][2:]

nlu_fallback = bot_response[bot_response['response_type'] == "nlu_fallback"].values[0][2:]

class Model:
    def __init__(self, url: str) -> None:
        self.agent = Agent.load(model_path=url)
        print("NLU model loaded")

    def message(self, message: str) -> str:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        print(result)
        return result['intent']['name'], result['intent']['confidence']


account_sid = os.environ['twillio_account_sid']
auth_token = os.environ['twillio_auth_token']
client = Client(account_sid, auth_token)

app = Flask(__name__)
app.secret_key = 'oaewedfpioasdofjaposjf'

def send_message(message):
    client.messages.create(to=request.values.get("From"), from_=request.values.get("To"), body=message)

@app.route("/", methods=["POST"])
def bot():
    user_msg = request.values.get('Body', '').lower()
    user_msg = " ".join(user_msg.split()) 
    if 'state' not in session or user_msg in greetings:
        session['state'] = 'start'
    print("Session state: ", session['state'])

    if session['state'] == 'start':
        send_message("👋 Hi there! I'm Lydiah, your helper for reporting positive or negative social and environmental issues happening where you live 🏘️. Our goal is to ensure timely response from relevant authorities, addressing concerns swiftly ⏰. By sharing positive issues happening in your community, we aim to inspire people in other areas, fostering unity and the spirit of 'Leave no one behind' 🌍.")
        session['state'] = "confirm_kenya"
        time.sleep(1)
        send_message("Just to let you know, I am designed to work exclusively within Kenya. Could you please confirm that you're currently in Kenya? (yes/no)")
    elif session['state'] == 'confirm_kenya':
        confirm_kenya = user_msg
        if confirm_kenya in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'language_selection'
            send_message('To continue, please choose your preferred language\n1. English\n2. Swahili\n3. Kikuyu')
        else:
            send_message("Apologies, but I don't have information on locations outside Kenya at the moment. If you have any other questions or need further assistance, feel free to ask. Goodbye!")
            session.pop('state', default=None)
        return "Language selection initiated."
    elif session['state'] == 'language_selection':
        language_choice = user_msg
        if language_choice in ['1', '2', '3']:
            session['language'] = int(language_choice)
            session['state'] = 'main_menu'
            send_message(introduction[session['language']-1])
            print(">> Main menu")
            time.sleep(1)
            send_message(main_menu[session['language']-1])
        else:
            send_message("Please enter a valid language choice (1, 2, 3).")
        return "Language selected."
    elif session['state'] == 'main_menu':
        menu_choice = user_msg
        if menu_choice in ['1', '2', '3', '4']:
            menu_choice = int(menu_choice)
            session['menu_choice'] = menu_choice
            if menu_choice == 1:
                session['state'] = 'option_1'
                send_message(app_steps[session['language']-1])
                print(">> download app")
                time.sleep(1)
                send_message(download_app_confirm[session['language']-1])
            elif menu_choice == 2:
                session['state'] = 'option_2'
                send_message(incident_confirm[session['language']-1])
            elif menu_choice == 3:
                session['state'] = 'option_3'
                send_message(general_misinformation[session['language']-1])
                print(">> misinformation")
                time.sleep(1)
                send_message(misinformation_confirm[session['language']-1])
            elif menu_choice == 4:
                session['state'] = 'option_4'
                send_message(location_welcome[session['language']-1])
                print(">> location selection")
                time.sleep(1)
                send_message(locations_list[session['language']-1])
        else:
            send_message("Please enter a valid menu choice (1, 2, 3, 4).")
        return "Menu choice selected."
    elif session['state'] == 'option_1':
        download_choice = user_msg
        if download_choice in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'end'
            send_message(download_app_steps[session['language']-1])
            time.sleep(1)
        print(">> anything else opt 1")
        session['state'] = "end"
        send_message(anything_else_dialog[session['language']-1])
        return "Option 1 closed"
    elif session['state'] == 'option_2':
        incident_msg = user_msg
        session['state'] = "end"
        model1 = Model(model1_path)
        intent, confidence = model1.message(incident_msg)
        if intent in incident_guides and confidence >= CONF_THRESH:
            session['state'] = "end"
            send_message(incident_guides[intent][session['language']-1])
        else:
            session['state'] = "end"
            send_message(nlu_fallback[session['language']-1])
        print(">> anything else opt 2")
        time.sleep(1)
        send_message(anything_else_dialog[session['language']-1])
        return "Option 2 closed"
    elif session['state'] == "option_3":
        misinformation_choice = user_msg
        if misinformation_choice in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'option_3_details'
            send_message(misinformation_details_dialog[session['language']-1])
        else:
            session['state'] = "end"
            send_message(anything_else_dialog[session['language']-1])
        return "Option 3 closed"
    elif session['state'] == 'option_3_details':
        misinformation_msg = user_msg
        session['state'] = "end"
        model2 = Model(model2_path)
        intent, confidence = model2.message(misinformation_msg)
        if intent in misinformation_guides and confidence >= CONF_THRESH:
            session['state'] = "end"
            send_message(misinformation_guides[intent][session['language']-1])
        else:
            session['state'] = "end"
            send_message(nlu_fallback[session['language']-1])
        print(">> anything else opt 3")
        time.sleep(1)
        send_message(anything_else_dialog[session['language']-1])
        return "Option 3 details closed"
    elif session['state'] == 'option_4':
        location_choice = user_msg
        if location_choice in ['1', '2', '3', '4', '5']:
            session['state'] = 'option_4_interest'
            session['location'] = location_choice
            send_message(interest_list[session['language']-1])
        else:
            send_message("Please enter a valid location choice (1, 2, 3, 4, 5).")
        return "Location selected."
    elif session['state'] == 'option_4_interest':
        interest_choice = user_msg
        if interest_choice in ['1', '2', '3']:
            interest_choice = int(interest_choice)
            session['state'] = 'end'
            send_message(interest_details[interest_choice][session['language']-1])
            session.pop('location', default=None)
            print(">> anything else opt 4")
            time.sleep(1)
            send_message(anything_else_dialog[session['language']-1])
        else:
            send_message(f"Please enter a valid interest choice (1, 2, 3)")
    elif session['state'] == 'end':
        anything_else_choice = user_msg
        if anything_else_choice in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'main_menu'
            send_message(main_menu[session['language']-1])
        else:
            send_message(goodbye[session['language']-1])
            session.pop('state', default=None)
        return "Session complete"
    return ""
