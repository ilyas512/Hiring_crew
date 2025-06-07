from pymongo import MongoClient
from crewai.tools import BaseTool
from src.config.settings import MONGO_URI

class JobOfferFetcher(BaseTool):
    name: str = "Job Offer Fetcher"
    description: str = "Fetches the latest job offer (title, description, and ID)."

    def _run(self):
        client = MongoClient(MONGO_URI)
        db = client['recrutement']
        offer = db['offre'].find_one(sort=[("createdAt", -1)])
        if not offer:
            return {"error": "No offer found."}

        return {
            "id": str(offer["_id"]),
            "title": offer.get("title", ""),
            "description": offer.get("description", "")
        }
