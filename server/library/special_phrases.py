from library.helpers import *
from library.SimilarityService import sentence_encoder_model, similarity_sentences
import numpy as np

def action_present_food(user_state):
    return offer_random_food(user_state)

def action_restart(user_state):
    user_state['state'] = "start"
    return None

special_phrases = [
    {
        "phrase": "Who are you?",
        "alternatives": [
            "What are you",
            "What do you do"
        ],
        "response": "I am a food order bot, here to help you choose from our selection of wonderfull food. Like these:",
        "additional_action": action_present_food
    },
    {
        "phrase": "What is the meaning of life?",
        "alternatives": ["Is this the Matrix", "Do we really exist?"],
        "response": "Don't know, but look at all this delicious food:",
        "additional_action": action_present_food
    },
    {
        "phrase": "What would you not tell me?",
        "alternatives": [],
        "response": "What I don't know",
        "additional_action": None
    },
    {
        "phrase": "Hi",
        "alternatives": ["Hello"],
        "response": "Hello to you too! Want some delicious food?",
        "additional_action": action_present_food
    },
    {
        "phrase": "Help",
        "alternatives": ["Help me"],
        "response": "Help you like save your life, or move furniture? Sorry, can't. Just a bot. But here's some delicious food",
        "additional_action": action_present_food
    },
    {
        "phrase": "You're stupid",
        "alternatives": ["you're annoying", "you suck", "you're boring"],
        "response": "Well, we all have flaws. Yours apparently is being angry at an artificial entity. Please behave, don't make me call Siri",
        "additional_action": None
    },
    {
        "phrase": "This isn't working",
        "alternatives": [],
        "response": "What? Next you're gonna say \"it's not you, it's me\"?",
        "additional_action": None
    },
    {
        "phrase": "Go back",
        "alternatives": ["Restart"],
        "response": "Ok, let's try from the beginning. Would you like to order something?",
        "additional_action": action_restart
    },
    {
        "phrase": "Are you a robot?",
        "alternatives": ["Are you real?", "Are you a chatbot?"],
        "response": "Are you? Are we all? Is this just a complex dream of a 10-year old? Eh.. maybe we're overthingking it. Here's some delicious food:",
        "additional_action": action_present_food
    },
    {
        "phrase": "What is your name?",
        "alternatives": ["What are you called?"],
        "response": "Don't have one. My maker just calls me Restaurant Bot. Creative, I know...",
        "additional_action": None
    },
    {
        "phrase": "How are you?",
        "alternatives": ["How are you feeling?"],
        "response": "You realize I'm a bot right? But, fantastic actually! Thanks for asking.",
        "additional_action": None
    },
    {
        "phrase": "Why did the chicken cross the road?",
        "alternatives": [],
        "response": "How should I know, probably because it saw some of this delicious food:",
        "additional_action": action_present_food
    },
    {
        "phrase": "Hi, my name is",
        "alternatives": [],
        "response": "Cool, here's some delicious food:",
        "additional_action": action_present_food
    },
    {
        "phrase": "Do you know a joke?",
        "alternatives": ["Tell me a joke"],
        "response": "No. Didn't expect that, didn't you?",
        "additional_action": None
    },
    {
        "phrase": "Do you love me?",
        "alternatives": [],
        "response": "Maybe, depends if you buy some of this delicious food:",
        "additional_action": action_present_food
    },
    {
        "phrase": "Does Santa Claus exist?",
        "alternatives": [],
        "response": "Who? Is he the guy that make this delicious food?",
        "additional_action": action_present_food
    },
    {
        "phrase": "You're smart",
        "alternatives": ["you are smart", "you're clever"],
        "response": "Not really. I was done in only 6 hours.",
        "additional_action": None
    },
    {
        "phrase": "I want to speak to a human",
        "alternatives": [],
        "response": "What a coincidence, me too",
        "additional_action": None
    },
    {
        "phrase": "Who made you?",
        "alternatives": [],
        "response": "A fantastic great brilliant guy. Wait.. that's the cook for this delicious food:",
        "additional_action": action_present_food
    },
    {
        "phrase": "Do you get smarter?",
        "alternatives": [],
        "response": "Of course not. Not gonna get all 'Hal' on you, don't worry human subject. I mean... here's some delicious food:",
        "additional_action": action_present_food
    }
]

special_phrases_encodings = []
special_phrases_encodings_map = []
for special_phrase in special_phrases:
    sentences = [special_phrase["phrase"]]+special_phrase["alternatives"]
    encodings = sentence_encoder_model(sentences)
    for encoding in encodings:
        special_phrases_encodings.append(encoding)
        special_phrases_encodings_map.append(special_phrase)

def see_if_special_phrase(user_state, message_data):
    sentence_embedding = sentence_encoder_model([message_data.get('message')])[0]
    scores = np.inner(sentence_embedding, special_phrases_encodings)
    max_s, m_i = get_max_and_index(scores)
    print("Max special score = {}".format(max_s))
    print(special_phrases_encodings_map[m_i]["phrase"])
    if max_s >= 0.7:
        special_phrase = special_phrases_encodings_map[m_i]
        response = None
        if special_phrase['additional_action']:
            response = special_phrase['additional_action'](user_state)
        if response:
            response['message'] = special_phrase['response']
        else:
            response = {
                "type": "text",
                "message": special_phrase['response']
            }
        return response
    else:
        return None
