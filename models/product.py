import datetime
from mongoengine import Document, StringField, IntField, ListField

class Product(Document):
    product_id = IntField(required=True)
    product_name = StringField(required=True)
    product_description = StringField(required=True)
    product_category = StringField(required=True)
    average_rating = IntField()
    price = IntField()
    reviews = ListField(StringField())

    meta = {
        'collection': 'product'
    }
