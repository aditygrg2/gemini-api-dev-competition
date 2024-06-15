import datetime
from mongoengine import Document, StringField, IntField, ReferenceField, ListField, DateTimeField

class Address(Document):
    apartment_no = StringField(required=True)
    area_street = StringField(required=True)
    landmark = StringField(required=True)
    town_city = StringField(required=True)
    state = StringField(required=True)
    pincode = IntField(required=True)
    meta={
        'collection':'address'
    }