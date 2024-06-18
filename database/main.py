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
        #     ]
        # }
        try:
            analysis.update_one({"phoneNumber":phoneNumber},{"$push": {"call_sent": data}},upsert=True)
        except Exception as e:
            print(e)

    def get_trackers(self):
        return self.trackerCollection.find_one()
    
    def insert_tracker_analysis(self, data):
        try:
            self.trackerCollection.insert_one(data)
        except Exception as e:
            print(e)