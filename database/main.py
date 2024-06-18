from pymongo import MongoClient
import os

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

    def get_user(self, phoneNumber):
        return self.userCollection.find_one({"phoneNumber": phoneNumber})
    
    def get_user_data_for_verification(self, phoneNumber):
        fields = ['phone_no', 'name', 'town_city', 'state', 'pincode']
        projection = {field: 1 for field in fields}
        return self.userCollection.find_one({"phoneNumber": phoneNumber}, projection)

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
        return self.trackerCollection.find_one()
    
    def insert_tracker_analysis(self, phoneNumber, data):
        try:
            self.analysisCollection.update_one({"phoneNumber": phoneNumber},{"$push": {"trackers": data}},upsert=True)
        except Exception as e:
            print(e)