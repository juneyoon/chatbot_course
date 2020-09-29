from flask import Flask, request, jsonify
from rasa.nlu.model import Interpreter

DefaultInterpreter = Interpreter.load('nlu_data/models/default/nlu')
app = Flask("Interpreters")

@app.route('/default', methods=['POST'])
def default_interpret():
    content = request.json
    interpreted = DefaultInterpreter.parse(content['intent_text'])
    return jsonify(interpreted)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5060)
