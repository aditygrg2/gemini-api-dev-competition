import datetime
from mongoengine import Document, StringField, IntField, ReferenceField, ListField, DateTimeField

class Transaction(Document):
    transaction_id = StringField(required=True)
    transaction_status = StringField(required=True)
    payment_method = StringField(required=True)
    total_amount = IntField(required=True)
    timestamp = DateTimeField(required=True)

    meta={
        'collection':'transaction'
    }
    
