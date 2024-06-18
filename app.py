from enum import Enum
from mongoengine import connect
from dotenv import load_dotenv
import os
import models.address as Address, models.orders as Order, models.product as Product, models.transactionDetail as Transaction, models.user as User
from VerificationChain import VerificationChain, VerificationChainStatus
from DuringChain import DuringChain, DuringChainStatus
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
import subprocess
from database.main import Database
from sentiment_analysis.main import SentimentAnalysis

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")

recognizer = sr.Recognizer()
AudioSegment.converter = which("ffmpeg")

client = connect(host=os.environ['MONGO_URL'])
db = Database()
sentiment = SentimentAnalysis()

all_users = client.list_database_names()
print(all_users)

user_dict = {

}

class CallStatus(Enum):
    VerificationChainNotStarted = 0
    VerificationChainStarted = 1
    DuringChainStarted = 2

@socketio.on('send_audio')
def handle_audio(data):
    try:
        phone_number = data['phone_number']
        data = data['data']
        audio_data = base64.b64decode(data)

        phone_dict = {
            'call_status':  CallStatus.VerificationChainNotStarted,
            "verification_chain": None,
            "during_chain": None,
            "user_query": "",
        }

        user_dict[phone_number] = phone_dict
        
        with open(f'{phone_number}.mp3', 'wb') as audio_file:
            audio_file.write(audio_data)

        subprocess.call(['ffmpeg', '-i', f'{phone_number}.mp3', f'{phone_number}.wav'])
        
        with sr.AudioFile(f'{phone_number}.wav') as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print(text)

            # user_data = db.get_user(phoneNumber)
            user_data = """

                    [{      
                "name": "Raj Patel",
                "address": {
                "phone_number": 932489237
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

            print(user_dict)

            if(user_dict[phone_number]['call_status'] == CallStatus.VerificationChainNotStarted):
                user_dict[phone_number]['user_query'] = text
                user_dict[phone_number]['verification_chain'] = VerificationChain(user_data=user_data, user_query=text)
                chat = user_dict[phone_number]['verification_chain'].start_chat()
                print(chat)
                convert_to_audio_and_send(chat[1])
                user_dict[phone_number]['call_status'] = CallStatus.VerificationChainStarted
                
            elif(user_dict[phone_number]['call_status'] == CallStatus.VerificationChainStarted):
                response = user_dict[phone_number]['verification_chain'].send_message(text)

                chain_status = response[0]

                if(chain_status == VerificationChainStatus.NOT_VERIFIED):
                    convert_to_audio_and_send(response[1])
                    user_dict[phone_number]['call_status'] = CallStatus.VerificationChainNotStarted
                    

                elif(chain_status == VerificationChainStatus.IN_PROGRESS):
                    convert_to_audio_and_send(response[1])
                
                else:
                    print("During chain started")
                    user_dict[phone_number]['during_chain'] = DuringChain(user_data=user_data, user_query=user_dict[phone_number]['user_query'])
                    chat_instance = user_dict[phone_number]['during_chain'].initialize_model()
                    response = user_dict[phone_number]['during_chain'].start_chat()
                    handle_during_chain_conditions(response)
                    user_dict[phone_number]['call_status'] = CallStatus.DuringChainStarted

            else:
                response = user_dict[phone_number]['during_chain'].send_message(text)
                handle_during_chain_conditions(response)

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

def convert_to_audio_and_send(text):
    print("AI Text", text)
    tts = gTTS(text)
    audio_output_buffer = BytesIO()
    tts.write_to_fp(audio_output_buffer)
    audio_output_buffer.seek(0)

    emit('receive_audio', audio_output_buffer.getvalue(), binary=True)
    return "something"

def handle_during_chain_conditions(response, phone_number):
    status = response[0]
    reply = response[1]

    if(status == DuringChainStatus.AGENT_TRANSFERRED or status == DuringChainStatus.TERMINATED):
        user_dict[phone_number]['call_status'] = CallStatus.VerificationChainNotStarted
        
    convert_to_audio_and_send(reply)

socketio.run(app, debug=True, host='0.0.0.0', port=8000)