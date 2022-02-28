import pymongo
import base64
import bson
from bson.binary import Binary

# establish a connection to the database
connection = pymongo.MongoClient()

#get a handle to the test database
db = connection.test
file_meta = db.file_meta
file_used = "Headshot.jpg"

def main():
    coll = db.sample
    with open(file_used, "rb") as f:
        encoded = Binary(f.read())

    coll.insert({"filename": file_used, "file": encoded, "description": "test" })