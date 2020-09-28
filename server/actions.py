from library.helpers import *
from pprint import pprint

def process_message(user_state, message_data, connection_id):
    global global_steps
    current_step = global_steps['start']
    if global_steps.get(user_state['state']):
        current_step = global_steps[user_state['state']]

    response = current_step['action'](user_state, message_data, None)
    return response

def action_default(user_state, message_data, interpreted):
    return {
        "type": "text",
        "message": message_data['message']
    }


global_steps = {
    "start": {
        "interpretor": "DefaultInterpreter",
        "action": action_default
    }
}
