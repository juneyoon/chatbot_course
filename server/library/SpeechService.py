from google.cloud import speech_v1
import numpy as np
import io
import os
import time
import json
from google.cloud import texttospeech

speechToTextClient = speech_v1.SpeechClient()
language_code = "en-US"
sample_rate_hertz = 48000
encoding = speech_v1.RecognitionConfig.AudioEncoding.LINEAR16
config = {
    "language_code": language_code,
    #"alternative_language_codes": "ro",
    "sample_rate_hertz": sample_rate_hertz,
    "encoding": encoding,
    "model": 'default'
}

def parse_data(filename_weba, filename_wav):
    os.system("ffmpeg -i {} {} -y".format(filename_weba, filename_wav))
    content = None
    if os.path.exists(filename_wav):
        with io.open(filename_wav, "rb") as f:
            content = f.read()
            audio = speech_v1.RecognitionAudio(content=content)
            return audio
    return content

def speech_to_text(filename_weba, filename_wav):
    current_config = config
    #if data.get('step') and step_possibilities.get(data['step']):
    #    current_config['speech_contexts'] = [speech.SpeechContext(phrases=step_possibilities.get(data['step']))]
    audio = parse_data(filename_weba, filename_wav)
    if audio:
        response = speechToTextClient.recognize(request={"config": current_config, 'audio': audio})
        if response.results:
            result = response.results[0]
            if result.alternatives:
                return result.alternatives[0].transcript
    return None


client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code='en-GB-Wavenet-D',
    ssml_gender=texttospeech.SsmlVoiceGender.MALE)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.95,
    pitch=-2.5
)


audios = {}
with open("audios.json", 'r') as file:
    audios = json.load(file)

def convert_to_audio(text, prefix=""):
    global audios
    if text in audios:
        return audios[text]
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    uid = "{}{}".format(prefix, time.time())
    with open("../client/assets/audios/{}.mp3".format(uid), 'wb') as out:
        out.write(response.audio_content)

    audios[text] = uid
    with open('audios.json', 'w') as outfile:
        json.dump(audios, outfile)

    return uid
