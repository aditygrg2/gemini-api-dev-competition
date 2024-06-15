import datetime
from mongoengine import Document, StringField, IntField,BooleanField, ReferenceField, ListField, DateTimeField
from .orders import Order
from .address import Address

class User(Document):
    phone_no=IntField(required=True)
    name= StringField(required=True)
    address = ReferenceField(Address)
    email = StringField(required=True)
    subscriptionStatus = BooleanField(default=False)
    previousOrders = ListField(ReferenceField(Order))

    meta = {
        'collection':'User'
    }