from flask import Flask, render_template, session, request, jsonify
import json
import ssl
import time
import io
from library.SpeechService import speech_to_text
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/audio_process', methods=['POST'])
def audio_process():
    uploaded_file = request.files['audio_data']
    language_code = request.form.get('language_code')
    state = request.form.get('state')
    t = time.time()
    filename_weba = "audio_files/{}.weba".format(t)
    filename_wav = "audio_files/{}.wav".format(t)
    if uploaded_file.filename != '':
        uploaded_file.save(filename_weba)

    response = speech_to_text(language_code, state, filename_weba, filename_wav)
    return jsonify({"response": response})


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, ssl_context=ssl_context)
