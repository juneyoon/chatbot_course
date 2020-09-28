import copy
import random
import re
import json

STATE_DEFAULT = {
    "state": "start",
    "order": []
}

def new_state():
    state = copy.deepcopy(STATE_DEFAULT)
    return state
