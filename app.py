from mongoengine import connect
from dotenv import load_dotenv
import os
import models.address as Address, models.orders as Order, models.product as Product, models.transactionDetail as Transaction, models.user as User
import json
from bson.json_util import dumps
from flask import Flask
from flask_socketio import SocketIO, emit
from io import BytesIO
import speech_recognition as sr
from gtts import gTTS
from pydub.utils import which
from pydub import AudioSegment
from flask_cors import CORS
from pydub.playback import play
import base64
import wave

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")

recognizer = sr.Recognizer()
AudioSegment.converter = which("ffmpeg")

client = connect(host=os.environ['MONGO_URL'])

all_users = client.list_database_names()
print(all_users)

@socketio.on('send_audio')
def handle_audio(data):
    try:
        audio_data = base64.b64decode(data)
        
        with open('received_audio.wav', 'wb') as audio_file:
            audio_file.write(audio_data)
        
        # Recognize the audio
        with sr.AudioFile('received_audio.wav') as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")

            # Process the text (you can add your processing logic here)
            processed_text = f"Processed: {text}"
            print(f"Processed text: {processed_text}")

            # Convert text to audio
            tts = gTTS(processed_text)
            audio_output_buffer = BytesIO()
            tts.write_to_fp(audio_output_buffer)
            audio_output_buffer.seek(0)

            # Send back the audio
            emit('receive_audio', base64.b64encode(audio_output_buffer.read()))

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

socketio.run(app, debug=True, host='0.0.0.0', port=8000)