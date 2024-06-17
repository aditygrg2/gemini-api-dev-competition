from enum import Enum
from mongoengine import connect
from dotenv import load_dotenv
import os
import models.address as Address, models.orders as Order, models.product as Product, models.transactionDetail as Transaction, models.user as User
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from VerificationChain import VerificationChain, VerificationChainStatus
from DuringChain import DuringChain, DuringChainStatus
from flask_socketio import SocketIO, emit
from io import BytesIO
import speech_recognition as sr
from gtts import gTTS
from pydub.utils import which
from pydub import AudioSegment
from flask import request
from flask_cors import CORS
import base64
import subprocess

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")

recognizer = sr.Recognizer()
AudioSegment.converter = which("ffmpeg")

client = connect(host=os.environ['MONGO_URL'])

all_users = client.list_database_names()
print(all_users)

class CallStatus(Enum):
    VerificationChainNotStarted = 0
    VerificationChainStarted = 1
    DuringChainStarted = 2

class UserSession:
    def __init__(self, sid):
        self.sid = sid
        self.room = sid
        self.call_status = CallStatus.VerificationChainNotStarted
        self.verification_chain = None
        self.during_chain = None
        self.user_query = ""

    def handle_audio(self, data):
        try:
            audio_data = base64.b64decode(data)
            
            with open(f'audios/{self.sid}.mp3', 'wb') as audio_file:
                audio_file.write(audio_data)

            subprocess.call(['ffmpeg', '-i', f'audios/{self.sid}.mp3', f'audios/{self.sid}.wav'])
            
            with sr.AudioFile(f'audios/{self.sid}.wav') as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                print(text)

                # Perform a Mongo Query here.

                user_data = """
                User Phone Number: 932489237


                    [{      
                "name": "Raj Patel",
                "address": {
                "apartment_no": "223, Suryasthali Appartment",
                "area_street": "Manavta Nagar",
                "landmark": "Hanuman Mandir",
                "town_city": "Bengaluru",
                "state": "Karnataka",
                "pincode": 530068
                },
                "email": "raja23@gmail.com",
                "subscriptionStatus": false,
                "previousOrders": [
                    {
                "order_id": “20234435843-1107”,
                "status": "Delivered",
                "transaction": {
                "transaction_id": "txn123dsafasd",
                "status": "Successful",
                "payment_method": "Amazon Pay",
                "total_amount": 3000,
                "timestamp": {
                    "$date": "2024-06-14T18:55:34.443Z"
                }
                },
                "items": [
                "product_id": 3247387,
                "name": "HRX Oversized T-Shirt",
                "description": "Cotton-Comfy fit Oversized T-Shirt",
                "category": "Clothing-Men-TShirt",
                "average_rating": 3,
                "price": 399,
                "reviews": [
                    "Very Comfortable and Affordable",
                    "Cheap and affordable",
                    "Don't BUY AT ALLLL"
                ]
                ],
                """

                if(self.call_started == CallStatus.VerificationChainNotStarted):
                    self.user_query = text
                    self.verification_chain = VerificationChain(user_data=user_data)
                    chat = self.verification_chain.start_chat()
                    self.convert_to_audio_and_send(chat)
                    self.call_status = CallStatus.VerificationChainStarted
                
                elif(self.call_started == CallStatus.VerificationChainStarted):
                    response = self.verification_chain.send_message(text)

                    chain_status = response[0]

                    if(chain_status == VerificationChainStatus.NOT_VERIFIED):
                        self.convert_to_audio_and_send(response[1])
                        self.call_status(CallStatus.VerificationChainNotStarted)
                        handle_disconnect()

                    elif(chain_status == VerificationChainStatus.IN_PROGRESS):
                        self.convert_to_audio_and_send(response[1])
                    
                    else:
                        self.during_chain = DuringChain(user_data=user_data, user_query=self.user_query)
                        chat_instance = self.during_chain.initialize_model()
                        response = self.during_chain.start_chat()
                        self.handle_during_chain_conditions(response)
                        self.call_status = CallStatus.DuringChainStarted

                else:
                    response = self.during_chain.send_message(text)
                    self.handle_during_chain_conditions(response)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    def convert_to_audio_and_send(self, text):
        print("AI Text", text)
        tts = gTTS(text)
        audio_output_buffer = BytesIO()
        tts.write_to_fp(audio_output_buffer)
        audio_output_buffer.seek(0)

        emit('receive_audio', audio_output_buffer.getvalue(), binary=True, room = self.sid)

    def handle_during_chain_conditions(self, response):
        status = response[0]
        reply = response[1]

        if(status == DuringChainStatus.AGENT_TRANSFERRED or status == DuringChainStatus.TERMINATED):
            self.call_status = CallStatus.VerificationChainNotStarted
            
        self.convert_to_audio_and_send(reply)


user_sessions = {}

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    user_sessions[sid] = UserSession(sid)
    join_room(sid)
    print(f"User {sid} connected and joined room {sid}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in user_sessions:
        del user_sessions[sid]
    leave_room(sid)
    print(f"User {sid} disconnected and left room {sid}")

@socketio.on('send_audio')
def handle_audio(data):
    sid = request.sid
    if sid in user_sessions:
        audio_data = base64.b64decode(data)
        user_sessions[sid].handle_audio(audio_data)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)