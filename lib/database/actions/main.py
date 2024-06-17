from pymongo import MongoClient

class Database():
    def __init__(self) -> None:
        self.db = MongoClient('mongodb+srv://')['amazon']
        self.userCollection = self.db['users']
        self.productCollection = self.db['products']
        pass

    def getUserDetails(mobileNumber):
        pass