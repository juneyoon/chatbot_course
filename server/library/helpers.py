import copy
import random
import re
import json
import requests

from library.FoodFilter import FoodFilterClass
from google.cloud import translate
from library.SpeechService import convert_to_audio

STATE_DEFAULT = {
    "state": "start",
    "order": [],
    "FoodFilter": None,
    "history": [],
    "language": "en"
}

def new_state():
    state = copy.deepcopy(STATE_DEFAULT)
    state['FoodFilter'] = FoodFilterClass()
    return state

def interpret_service(interpreter, intent_text):
    route_map = {
        "DefaultInterpreter": "default",
        "MenuOrHelpInterpreter": "menu_or_help",
        "ListOptionsInterpreter": "list_options",
        "OrderInterpreter": "order",
        "FinalOrderInterpreter": "final_order"
    }

    if interpreter not in route_map:
        raise Exception("not ok")

    route = route_map[interpreter]

    try:
        r = requests.post("http://localhost:5060/{}".format(route),
                            json={"intent_text": intent_text})
    except requests.ConnectionError:
        raise Exception("Error on interpret server connection")

    res = r.json()

    return res


def filter_parse_and_search(user_state, interpreted):
    results = user_state['FoodFilter'].extract_filters(interpreted)
    if len(results) <= 15 and len(results)>=1:
        message = parse_search_results(results)
        user_state['current_options'] = results
        user_state['state'] = "list_options"
        return message
    elif len(results) > 15:
        user_state['state'] = "menu_or_help"
        return {
            "type": "text",
            "message": "Too broad search. Would you like me to help you choose?"
        }
    else:
        user_state['state'] = "menu_or_help"
        return {
            "type": "text",
            "message": "Nothing found. Would you like me to help you choose?"
        }

def parse_search_results(results):
    options = results.copy()
    if len(options) > 10:
        options = random.sample(options, k=10)
    message = "Here is what we have:"

    return {
        "type": "list_options",
        "message": message,
        "options": options
    }

def treat_decline_case(user_state):
    if user_state.get('order'):
        user_state['state'] = "confirm_order"
        return generate_order_confirm(food)
    else:
        user_state['state'] = "canceled"
        return {
            "type": "text",
            "message": "That’s ok, I’ll be here when you need me!"
        }

def generate_order_confirm(food):
    food_str = ""
    price = 0
    if len(food)>1:
        food_str = ", ".join([f['name'] for f in food])
    else:
        food_str = food[0]['name']
    for f in food:
        price += f['price']
    return {
        "type": "text",
        "message": "So you want {} for {}$?".format(food_str, price)
    }

def get_max_and_index(scores):
    max_s = 0
    m_i = -1
    for i in range(0, len(scores)):
        if scores[i] > max_s:
            max_s = scores[i]
            m_i = i

    return max_s, m_i

def list_options_generate(user_state):
    results = user_state['FoodFilter'].search()
    user_state['current_options'] = results
    message = parse_search_results(results)

    user_state['state'] = "list_options"
    return message


def ask_disambiguisation(user_state, interpreted, current_step_name, disambiguisations):
    if disambiguisations.get(current_step_name):
        text_1 = generate_disambiguisation_text(interpreted, disambiguisations[current_step_name].get(interpreted['intent_ranking'][0]['name']))
        text_2 = generate_disambiguisation_text(interpreted, disambiguisations[current_step_name].get(interpreted['intent_ranking'][1]['name']))
        if text_1 and text_2:
            user_state['disambiguisation'] = {
                "intent_1": interpreted['intent_ranking'][0]['name'],
                "intent_2": interpreted['intent_ranking'][1]['name']
            }
            return {
                "type": "text",
                "message": "Sorry, I'm not sure what you meant. Did you mean \"{}\", or \"{}\"?".format(text_1, text_2)
            }
    return None


def generate_disambiguisation_text(interpreted, text):
    txt = text
    entities = re.findall("\[[a-z_]+\]", txt)
    if entities:
        if len(entities) > 1:
            for entity in entities:
                entity_replacements = []
                for i_entity in interpreted['entities']:
                    if i_entity['entity'] == entity[1:-1]:
                        entity_replacements.append(i_entity['value'])
                if entity_replacements:
                    txt = txt.replace(entity, compose_text_from_list(entity_replacements))
                else:
                    txt = txt.replace(entity, "[x]")
        else:
            entity = entities[0]
            entity_replacements = []
            for i_entity in interpreted['entities']:
                entity_replacements.append(i_entity['value'])
            if entity_replacements:
                txt = txt.replace(entity, compose_text_from_list(entity_replacements))
            else:
                txt = txt.replace(entity, "[x]")
    return txt


def compose_text_from_list(entities):
    if len(entities) > 2:
        text = ", ".join(entities[:-1])
        text += " and " + entities[-1]
        return text
    return ", ".join(entities)


def log_history(user_state, connection_id, interpreted, response):
    user_state['history'].append({
        "from": "user",
        "message": interpreted['text'],
        "intent": interpreted['intent']['name'],
        "interpreted": interpreted,
    })
    bot_log = {
        "from": "bot",
        "message": response.get('message')
    }
    if user_state.get('disambiguisation'):
        bot_log['disambiguisation'] = user_state['disambiguisation']
        user_state['disambiguisation'] = None
    user_state['history'].append(bot_log)
    with open("logs/conversations/{}.json".format(connection_id), 'w') as outfile:
        json.dump(user_state['history'], outfile, indent=4)


project_id = "thematic-bloom-275007"
translate_parent = 'projects/{}'.format(project_id)
translateClient = translate.TranslationServiceClient()

def translate(text, lang_from, lang_to):
    if len(text)>128:
        text = text[:128]
    response = translateClient.translate_text(
    parent=translate_parent,
    contents=text,
    mime_type='text/plain',  # mime types: text/plain, text/html
    source_language_code=lang_from,
    target_language_code=lang_to)

    res = []
    for line in response.translations:
        res.append(line.translated_text)

    return res


def process_translation_from_user(user_state, message_data):
    if user_state['language'] != "en" and message_data.get("message"):
        translated = translate([message_data["message"]], user_state['language'], "en")
        if translated:
            message_data['message'] = translated[0]

def process_translation_to_user(user_state, response):
    if user_state['language'] != "en" and response.get("message"):
        translated = translate([response["message"]], "en", user_state['language'])
        if translated:
            response['message'] = translated[0]
    return response

def add_audio(response):
    if response.get('message'):
        uid = convert_to_audio(response.get('message'))
        response['audio'] = uid
    return response
