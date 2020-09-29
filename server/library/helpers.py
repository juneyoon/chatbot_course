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

def interpret_service(interpretor, intent_text):
    route_map = {
        "DefaultInterpreter": "default",
    }

    if interpretor not in route_map:
        raise Exception("not ok")

    route = route_map[interpretor]

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
