from library.helpers import *
from pprint import pprint
from library.SimilarityService import similarity_sentences
from library.special_phrases import see_if_special_phrase

def process_message(user_state, message_data, connection_id):
    global global_steps
    current_step = global_steps['start']
    if global_steps.get(user_state['state']):
        current_step = global_steps[user_state['state']]

    process_translation_from_user(user_state, message_data)
    interpreted = interpret_service(current_step['interpreter'], message_data.get('message'))

    special_phrase_result = see_if_special_phrase(user_state, message_data)
    if special_phrase_result:
        return transform_user_response(user_state, connection_id, interpreted, special_phrase_result)

    response = verify_interpret_result(user_state, interpreted, user_state['state'])
    if response:
        return transform_user_response(user_state, connection_id, interpreted, response)

    response = current_step['action'](user_state, message_data, interpreted)
    return transform_user_response(user_state, connection_id, interpreted, response)

def verify_interpret_result(user_state, interpreted, current_step_name):
    global disambiguations
    print("Action - {}".format(user_state['state']))
    pprint(interpreted)

    if interpreted['intent']['confidence'] >= 0.8:
        return None

    if len(interpreted['intent_ranking']) > 1:
        sum_first2 = interpreted['intent_ranking'][0]['confidence'] + interpreted['intent_ranking'][1]['confidence']
        if sum_first2 >= 0.8:
            result = ask_disambiguisation(user_state, interpreted, current_step_name, disambiguations)
            if result:
                return result

    return {
        "type": "text",
        "message": "Sorry I couldn't understand what you meant. I'm still learning, can you please try again more simple and precise in your meaning?"
    }

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
        sim_scores = similarity_sentences(options, entity)
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
        sim_scores = similarity_sentences(options, entity)
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
        sim_scores = similarity_sentences(options, entity)
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

def action_confirm_order(user_state, message_data, interpreted):
    if interpreted['intent']['name'] == "yes_simple":
        user_state['state'] = "final_order"
        return {
            "type": "text",
            "message": "Anything else?"
        }
    if interpreted['intent']['name'] == "decline":
        return list_options_generate(user_state)
    if interpreted['intent']['name'] == "not_x":
        food = user_state['order'].copy()
        for entity in interpreted['entities']:
            filter_entity = user_state['FoodFilter'].find_entity(entity['value'], ignore_names=False)
            if filter_entity:
                for i in range(0, len(food)):
                    if food[i]['name'] == filter_entity['value']:
                        food.pop(i)
                        break
        if food:
            user_state['order'] = food
            user_state['state'] = "confirm_order"
            return generate_order_confirm(user_state['order'])
        else:
            return list_options_generate(user_state)
    if interpreted['intent']['name'] == "just_y":
        food = user_state['order'].copy()
        new_food = []
        for entity in interpreted['entities']:
            filter_entity = user_state['FoodFilter'].find_entity(entity['value'], ignore_names=False)
            if filter_entity:
                for i in range(0, len(food)):
                    if food[i]['name'] == filter_entity['value']:
                        new_food.append(food[i])
                        break
        if new_food:
            user_state['order'] = new_food
            user_state['state'] = "confirm_order"
            return generate_order_confirm(user_state['order'])
        else:
            return list_options_generate(user_state)
    if interpreted['intent']['name'] == "just_y+not_x":
        food = user_state['order'].copy()
        new_food = []

        for entity in interpreted['entities']:
            filter_entity = user_state['FoodFilter'].find_entity(entity['value'], ignore_names=False)
            if filter_entity:
                for i in range(0, len(food)):
                    if food[i]['name'] == filter_entity['value']:
                        if entity['entity'] == "order_item_yes":
                            new_food.append(food[i])
                        break
        if new_food:
            user_state['order'] = new_food
            user_state['state'] = "confirm_order"
            return generate_order_confirm(user_state['order'])
        else:
            return list_options_generate(user_state)

def action_final_order(user_state, message_data, interpreted):
    if interpreted['intent']['name'] == "yes_simple":
        user_state['state'] = "start"
        return {
            "type": "text",
            "message": "What else would you like?"
        }
    if interpreted['intent']['name'] == "finish":
        user_state['state'] = "ordered"
        return {
            "type": "text",
            "message": "Ok, thanks for your order! Will be ready in 30 minutes"
        }
    if interpreted['intent']['name'] == "yes_x_y":
        user_state['FoodFilter'].reset_filters()
        return filter_parse_and_search(user_state, interpreted)

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
    },
    "confirm_order": {
        "interpreter": "OrderInterpreter",
        "action": action_confirm_order
    },
    "final_order": {
        "interpreter": "FinalOrderInterpreter",
        "action": action_final_order
    }
}

disambiguations = {
    "start": {
        "yes_simple": "Yes, I want to make an order",
        "yes_not_sure": "Not sure what I want",
        "yes_x_y": "Yes, I want [order_item]",
        "decline": "don't want anything"
    },
    "ask_mood": {
        "yes_not_sure": "Not sure, what do you have?",
        "yes_x_y": "I want [order_item]",
        "decline": "don't want anything"
    },
    "menu_or_help": {
        "help": "Help me find something else",
        "yes_simple": "Yes, help me",
        "yes_menu": "Yes, I want the menu",
        "yes_x_y": "I only want the [order_item]",
        "decline": "don't want anything"
    },
    "list_options": {
        "something_else": "Do you have [order_item]?",
        "yes_x_y": "I want [order_item]"
    },
    "confirm_order": {
        "decline": "Don't finish the order",
        "yes_simple": "Yes, finish the order",
        "just_y": "Keep only the [order_item_yes]",
        "not_x": "Remove the [order_item_no] from the order",
        "just_y+not_x": "Keep the [order_item_yes], remove the [order_item_no]"
    }
}
