from pymongo import MongoClient
import os

from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.environ['MONGO_URL'])
db = client['amazon_data']
userCollection = db['User']
analysis = db['analysis']
trackers = db['trackers']

class Database():
    def __init__(self) -> None:
        self.userCollection = userCollection
        self.analysisCollection = analysis
        self.trackerCollection = trackers

    def get_user(self, phone_number):
        projection = {
            '_id': 0
        }
        return self.userCollection.find_one({"phone_number": phone_number}, projection)
    
    def get_user_data_for_verification(self, phone_number):
        fields = ['phone_number', 'name', 'town_city', 'state', 'pincode']
        projection = {field: 1 for field in fields}
        projection['_id'] = 0
        return self.userCollection.find_one({"phone_number": phone_number}, projection)

    def insert_audio_analysis(self, phoneNumber, data):
        # {
        #     "phoneNumber":"",
        #     "call_st":[
        #         {
        #             "type":"AI",
        #             "sent":"hap",
        #             "file":"filepath"
        #         },
        #         {
        #             "type":"human",
        #             "sent":"hap",
        #             "file":"fielpath"
        #         },
        #     ],
        #     "trackers":[
        #         {
        #             "title":"Amazon great indian sale",
        #             "trackerCount":{
        #                 "winter":2,
        #                 "great":3
        #             }
        #         }
        #     ]
        # }
        try:
            analysis.update_one({"phoneNumber":phoneNumber},{"$push": {"call_sent": data}},upsert=True)
        except Exception as e:
            print(e)

    def get_trackers(self):
        return self.trackerCollection.find_one(None,{"_id":0})
    
    def insert_tracker_analysis(self, phoneNumber, data):
        try:
            self.analysisCollection.update_one({"phoneNumber": phoneNumber},{"$push": {"trackers": data}},upsert=True)
        except Exception as e:
            print(e)