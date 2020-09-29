from library.helpers import *
from pprint import pprint

def process_message(user_state, message_data, connection_id):
    global global_steps
    current_step = global_steps['start']
    if global_steps.get(user_state['state']):
        current_step = global_steps[user_state['state']]

    interpreted = interpret_service(current_step['interpreter'], message_data.get('message'))
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
        user_state['menu'] = user_state['specials']
        return {
            "type": "text",
            "message": "Ok then, I can help you. For today’s special we have {} with 10$. Is that ok for you, or would you like me to help you find something else?".format(specials)
        }

    if interpreted['intent']['name'] == "decline":
        return treat_decline_case(user_state)

def action_ask_mood(user_state, message_data, interpreted):
    if interpreted['intent']['name'] == "yes_not_sure" or interpreted['intent']['name'] == "yes_simple":
        user_state['state'] = "menu_or_help"
        specials = user_state['FoodFilter'].generate_specials(user_state)
        user_state['menu'] = user_state['specials']
        return {
            "type": "text",
            "message": "Ok then, I can help you. For today’s special we have {} with 10$. Is that ok for you, or would you like me to help you find something else?".format(specials)
        }

    if interpreted['intent']['name'] == "yes_x_y":
        user_state['FoodFilter'].reset_filters()
        return filter_parse_and_search(user_state, interpreted)

    if interpreted['intent']['name'] == "decline":
        return treat_decline_case(user_state)


def action_menu_or_help(user_state, message_data, interpreted):
    if interpreted['intent']['name'] == "help" or interpreted['intent']['name'] == "yes_simple":
        user_state['state'] = "help_category"
        return {
            "type": "text",
            "message": "Would you like a meal, a soup, a pizza or maybe something sweet?"
        }

    if interpreted['intent']['name'] == "yes_menu":
        user_state['order'].extend(user_state['menu'])
        user_state['state'] = "confirm_order"
        return generate_order_confirm(user_state['order'])

    if interpreted['intent']['name'] == "yes_x_y":
        user_state['FoodFilter'].reset_filters()
        return filter_parse_and_search(user_state, interpreted)

    if interpreted['intent']['name'] == "decline":
        return treat_decline_case(user_state)

def action_help_category(user_state, message_data, interpreted):
    options = ["meal", "sweet", "soup", "pizza"]
    entities = []
    if interpreted['entities']:
        for entity in interpreted['entities']:
            entities.append(entity['value'])
    else:
        entities = message_data['message'].split()

    for entity in entities:
        sim_scores = user_state['FoodFilter'].similarity_sentences(options, entity)
        max_s, max_index = get_max_and_index(sim_scores)
        if max_s >= 0.5:
            filter = {
                'score': max_s,
                'type': 'categories',
                'value': options[max_index]
            }
            user_state['FoodFilter'].add_filter(filter)

    user_state['state'] = "help_country"
    return {
        "type": "text",
        "message": "Do you preffer a specific cuisine? We have French, Japanese, Italian and Mexican."
    }

def action_help_country(user_state, message_data, interpreted):
    options = ["France", "Japan", "Italy", "Mexico"]
    entities = []
    if interpreted['entities']:
        for entity in interpreted['entities']:
            entities.append(entity['value'])
    else:
        entities = message_data['message'].split()

    for entity in entities:
        sim_scores = user_state['FoodFilter'].similarity_sentences(options, entity)
        max_s, max_index = get_max_and_index(sim_scores)
        if max_s >= 0.5:
            filter = {
                'score': max_s,
                'type': 'countries',
                'value': options[max_index]
            }
            user_state['FoodFilter'].add_filter(filter)

    user_state['state'] = "help_restrictions"
    return {
        "type": "text",
        "message": "Do you have any food restrictions?"
    }

def action_help_restrictions(user_state, message_data, interpreted):
    options = ["gluten-free", "vegan", "egg-free", "vegetarian", "dairy-free"]
    entities = []
    if interpreted['entities']:
        for entity in interpreted['entities']:
            entities.append(entity['value'])
    else:
        entities = message_data['message'].split()

    for entity in entities:
        sim_scores = user_state['FoodFilter'].similarity_sentences(options, entity)
        max_s, max_index = get_max_and_index(sim_scores)
        if max_s >= 0.5:
            filter = {
                'score': max_s,
                'type': 'specials',
                'value': options[max_index]
            }
            user_state['FoodFilter'].add_filter(filter)

    results = user_state['FoodFilter'].search()
    user_state['current_options'] = results
    message = parse_search_results(results)

    user_state['state'] = "list_options"
    return message

def action_list_options(user_state, message_data, interpreted):
    if interpreted['intent']['name'] == "yes_x_y":
        food = []

        not_clear = False
        if interpreted['entities']:
            not_clear, food = user_state['FoodFilter'].search_in(user_state['current_options'], interpreted['entities'])
        else:
            not_clear = True

        if not_clear:
            user_state['state'] = "list_options"
            return {
                "type": "text",
                "message": "Sorry couldn't understand what you meant, please be more precise in your choice. Or do you want something else?"
            }
        else:
            user_state['order'].extend(food)
            user_state['state'] = "confirm_order"
            return generate_order_confirm(user_state['order'])

    if interpreted['intent']['name'] == "something_else":
        if interpreted['entities']:
            not_clear, food = user_state['FoodFilter'].search_in(user_state['current_options'], interpreted['entities'])
            if len(food)>=1:
                user_state['current_options'] = food
                return parse_search_results(food)
            else:
                return {
                    "type": "text",
                    "message": "Nothing found sorry"
                }
        else:
            user_state['state'] = "start"
            return {
                "type": "text",
                "message": "What would you like?"
            }
    if interpreted['intent']['name'] == "yes_simple":
        if len(user_state['current_options']) == 1:
            user_state['order'].extend(user_state['current_options'])
            user_state['state'] = "confirm_order"
            return generate_order_confirm(user_state['order'])
        else:
            message = list_options_generate(user_state)
            message['message'] = "Ok, please choose from here if you like anything"
            return message

global_steps = {
    "start": {
        "interpreter": "DefaultInterpreter",
        "action": action_default
    },
    "ask_mood": {
        "interpreter": "DefaultInterpreter",
        "action": action_ask_mood
    },
    "menu_or_help": {
        "interpreter": "MenuOrHelpInterpreter",
        "action": action_menu_or_help
    },
    "help_category": {
        "interpreter": "DefaultInterpreter",
        "action": action_help_category
    },
    "help_country": {
        "interpreter": "DefaultInterpreter",
        "action": action_help_country
    },
    "help_restrictions": {
        "interpreter": "DefaultInterpreter",
        "action": action_help_restrictions
    },
    "list_options": {
        "interpreter": "ListOptionsInterpreter",
        "action": action_list_options
    }
}
