from mongoengine import connect
from dotenv import load_dotenv
import os
import models.address as Address, models.orders as Order, models.product as Product, models.transactionDetail as Transaction, models.user as User
import json
from bson.json_util import dumps

load_dotenv()

client = connect(host=os.environ['MONGO_URL'])

all_users = client.list_database_names()
print(all_users)