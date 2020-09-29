from library.helpers import *
from pprint import pprint

def process_message(user_state, message_data, connection_id):
    global global_steps
    current_step = global_steps['start']
    if global_steps.get(user_state['state']):
        current_step = global_steps[user_state['state']]

    interpreted = interpret_service(current_step['interpretor'], message_data.get('message'))
    print("Action - {}".format(user_state['state']))
    pprint(interpreted)

    response = current_step['action'](user_state, message_data, interpreted)
    return response

def action_default(user_state, message_data, interpreted):
    if interpreted['intent']['name'] == "yes_simple":
        return {
            "type": "text",
            "message": "What are you in the mood for?"
        }

    if interpreted['intent']['name'] == "yes_x_y":
        user_state['FoodFilter'].reset_filters()
        return filter_parse_and_search(user_state, interpreted)

    if interpreted['intent']['name'] == "yes_not_sure":
        user_state['state'] = "menu_or_help"
        specials = user_state['FoodFilter'].generate_specials(user_state)
        user_state['menu'] = specials
        return {
            "type": "text",
            "message": "Ok then, I can help you. For today’s special we have {} with 10$. Is that ok for you, or would you like me to help you find something else?".format(specials)
        }

    if interpreted['intent']['name'] == "decline":
        return {
            "type": "text",
            "message": "That's ok, I'll be here when you need me!"
        }


global_steps = {
    "start": {
        "interpretor": "DefaultInterpreter",
        "action": action_default
    }
}
