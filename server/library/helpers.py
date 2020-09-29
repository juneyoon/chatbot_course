import copy
import random
import re
import json
import requests

from library.FoodFilter import FoodFilterClass

STATE_DEFAULT = {
    "state": "start",
    "order": [],
    "FoodFilter": None
}

def new_state():
    state = copy.deepcopy(STATE_DEFAULT)
    state['FoodFilter'] = FoodFilterClass()
    return state

def interpret_service(interpreter, intent_text):
    route_map = {
        "DefaultInterpreter": "default",
        "MenuOrHelpInterpreter": "menu_or_help"
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
