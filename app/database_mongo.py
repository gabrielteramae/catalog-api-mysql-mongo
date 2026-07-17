from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB", "catalogo_reviews")

_client = MongoClient(MONGO_URL)
mongo_db = _client[MONGO_DB_NAME]
reviews_collection = mongo_db["reviews"]
