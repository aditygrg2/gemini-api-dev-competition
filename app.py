from enum import Enum
from mongoengine import connect
from dotenv import load_dotenv
import os
import re
from pydub import AudioSegment
import datetime
import models.address as Address, models.orders as Order, models.product as Product, models.transactionDetail as Transaction, models.user as User
from VerificationChain import VerificationChain, VerificationChainStatus
from DuringChain import DuringChain, DuringChainStatus
from bson.json_util import dumps
from flask import Flask
from flask_socketio import SocketIO, emit
from io import BytesIO
from uuid import uuid4
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
from sentiment_analysis.main import SentimentTypes


load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")

recognizer = sr.Recognizer()
AudioSegment.converter = which("ffmpeg")
files = []

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

        if(phone_number not in user_dict.keys()):
            phone_dict = {
                'call_status':  CallStatus.VerificationChainNotStarted,
                "verification_chain": None,
                "during_chain": None,
                "user_query": "",
            }

            user_dict[phone_number] = phone_dict
        
        audio_data = base64.b64decode(data)
        u = uuid4()

        if(not os.path.exists(f"audios/{phone_number}")):
            os.mkdir(f"audios/{phone_number}")

        audio_name_mp3 = f"audios/{phone_number}/{u}.mp3"
        audio_name_wav = f"audios/{phone_number}/{u}.wav"
        
        with open(audio_name_mp3, 'wb') as audio_file:
            audio_file.write(audio_data)
            files.append(audio_name_mp3)

        senti = sentiment.analyze_audio_and_save(audio_name_mp3, False, phone_number)

        if(senti == SentimentTypes.NEGATIVE):
            if(user_dict[phone_number]['call_status'] == CallStatus.DuringChainStarted):
                del user_dict[phone_number]
                reply = """I am sorry that you are facing this. I am forwarding your call to the agent for better help."""
                convert_to_audio_and_send(reply, phone_number)

                handle_termination(phone_number)
                delete_files_in_folder()

                socketio.emit('finish', "agent_transfer")
                socketio.emit('disconnect')
                return

        subprocess.call(['ffmpeg', '-i', audio_name_mp3, audio_name_wav])
        
        with sr.AudioFile(audio_name_wav) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print("Human Said", text)

            user_data = str(db.get_user_data_for_verification(phone_number))
            print(user_data)
            # user_data = """
            #     "name": "Raj Patel",
            #     "phone_number": "9324899237"
            #     "town_city": "Bengaluru",
            #     "state": "Karnataka",
            #     "pincode": "530068"
            # """

            print(user_dict)

            if(user_dict[phone_number]['call_status'] == CallStatus.VerificationChainNotStarted):
                user_dict[phone_number]['user_query'] = text
                user_dict[phone_number]['verification_chain'] = VerificationChain(user_data=user_data, user_query=text, phone_number=phone_number)
                print("verification chain started")
                chat = user_dict[phone_number]['verification_chain'].start_chat()
                print("124", chat)
                user_dict[phone_number]['call_status'] = CallStatus.VerificationChainStarted
                convert_to_audio_and_send(chat[1], phone_number)
                
            elif(user_dict[phone_number]['call_status'] == CallStatus.VerificationChainStarted):
                response = user_dict[phone_number]['verification_chain'].send_message(text)
                print("130", response)

                chain_status = response[0]

                if(chain_status == VerificationChainStatus.NOT_VERIFIED):
                    convert_to_audio_and_send(response[1], phone_number)
                    user_dict[phone_number]['call_status'] = CallStatus.VerificationChainNotStarted
                    handle_termination(phone_number)
                    delete_files_in_folder()
                    
                elif(chain_status == VerificationChainStatus.IN_PROGRESS):
                    convert_to_audio_and_send(response[1], phone_number)
                
                else:
                    print("During chain started")
                    user_db_during = str(db.get_user(phone_number))
                    print(user_db_during)
                    user_dict[phone_number]['during_chain'] = DuringChain(user_data=user_db_during, user_query=user_dict[phone_number]['user_query'], sentiment=sentiment, phone_number=phone_number)
                    chat_instance = user_dict[phone_number]['during_chain'].initialize_model()
                    response = user_dict[phone_number]['during_chain'].start_chat()
                    user_dict[phone_number]['call_status'] = CallStatus.DuringChainStarted
                    handle_during_chain_conditions(response, phone_number, u)

            else:
                response = user_dict[phone_number]['during_chain'].send_message(text)
                handle_during_chain_conditions(response, phone_number, u)

    except sr.UnknownValueError:
        convert_to_audio_and_send("Can you please repeat? I am unable to understand your query.", phone_number)
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        convert_to_audio_and_send("Can you please repeat? I am unable to understand your query.", phone_number)
        print(f"Could not request results from Google Speech Recognition service; {e}")
    finally:
        try:
            user_dict[phone_number]['first_time'] = False
        except:
            pass


def convert_to_audio_and_send(text, phone_number):
    print("AI Text", text)
    text = text.replace("*", "")
    text = text.replace("`", "")
    text = text.replace("'", "")
    text = text.replace("/", "")
    tts = gTTS(text)
    audio_output_buffer = BytesIO()
    tts.write_to_fp(audio_output_buffer)
    audio_output_buffer.seek(0)

    u = uuid4()

    audio_path = f"audios/{phone_number}/{u}.mp3"
    audio = AudioSegment.from_file(audio_output_buffer, format="mp3")
    audio.export(audio_path, format="mp3")
    
    files.append(audio_path)
    sentiment.analyze_audio_and_save(audio_path, True, phone_number)

    emit('receive_audio', audio_output_buffer.getvalue(), binary=True)
    return "something"

def handle_during_chain_conditions(response, phone_number, u):
    status = response[0]
    reply = response[1]
    convert_to_audio_and_send(reply, phone_number)

    if(status == DuringChainStatus.AGENT_TRANSFERRED or status == DuringChainStatus.TERMINATED):
        handle_termination(phone_number)
        delete_files_in_folder()
        if(status == DuringChainStatus.AGENT_TRANSFERRED):
            socketio.emit('finish', "agent_transfer")
        else:
            socketio.emit('finish', "exit")
            
        del user_dict[phone_number]

def merge_audio_files(files, phone_number):
    combined = AudioSegment.empty()

    for file_path in files:
        if file_path.endswith(('.mp3', '.wav', '.ogg', '.flv', '.raw', '.aac', '.wma', '.flac')):
            audio = AudioSegment.from_file(file_path)
            combined += audio 

    combined.export(f"merged_audios/{phone_number}-{str(datetime.datetime.now())}.mp3", format="mp3")

def delete_files_in_folder():
    for file_name in files:
        try:
            if os.path.isfile(file_name):
                os.remove(file_name)
            else:
                print(f"{file_name} is not a file.")
        except Exception as e:
            print(f"Failed to delete {file_name}. Reason: {e}")

def handle_termination(phone_number):
    global files
    merge_audio_files(files, phone_number)
    files = []
    
socketio.run(app, debug=True, host='0.0.0.0', port=8000)