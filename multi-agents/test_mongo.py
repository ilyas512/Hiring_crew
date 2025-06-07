from pymongo import MongoClient
from src.config.settings import MONGO_URI
import json
from datetime import datetime
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def test_mongodb_connection():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client['recrutement']
        
        # Fetch all job offers, sorted by creation date (newest first)
        offers = list(db['offre'].find().sort("createdAt", -1))
        
        if offers:
            print("\nFound", len(offers), "job offers:")
            for i, offer in enumerate(offers, 1):
                print(f"\n{i}. Job Offer:")
                print(json.dumps(offer, indent=2, cls=JSONEncoder))
        else:
            print("\nNo job offers found in the database.")
            
        print("\nMongoDB connection successful!")
        
    except Exception as e:
        print(f"\nError connecting to MongoDB: {str(e)}")

if __name__ == "__main__":
    test_mongodb_connection() 