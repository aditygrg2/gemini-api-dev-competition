from database.actions.main import Database

class ConversationalChain():
    def __init__(self, mobileNumber: str) -> None:
        db = Database()
        self.userDetails = db.getUserDetails(mobileNumber)
        pass
    
    