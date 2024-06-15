import datetime
from mongoengine import Document, StringField, IntField, ReferenceField, ListField, DateTimeField
from .product import Product
from .transactionDetail import Transaction

class Order(Document):
    order_id = StringField(required=True)
    user_number = IntField(required=True)
    order_status = StringField(required=True)
    transaction = ReferenceField(Transaction)
    order_items = ListField(ReferenceField(Product))
    timestamp = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'order'
    }

