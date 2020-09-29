from flask import Flask, request, jsonify
from rasa.nlu.model import Interpreter

DefaultInterpreter = Interpreter.load('nlu_data/models/default/nlu')
MenuOrHelpInterpreter = Interpreter.load('nlu_data/models/menu_or_help/nlu')
app = Flask("Interpreters")

@app.route('/default', methods=['POST'])
def default_interpret():
    content = request.json
    interpreted = DefaultInterpreter.parse(content['intent_text'])
    return jsonify(interpreted)

@app.route('/menu_or_help', methods=['POST'])
def menu_or_help_interpret():
    content = request.json
    interpreted = MenuOrHelpInterpreter.parse(content['intent_text'])
    return jsonify(interpreted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5060)
