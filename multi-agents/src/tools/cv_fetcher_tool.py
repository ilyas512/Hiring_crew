import fitz
import gridfs
from pymongo import MongoClient
from bson import ObjectId
from crewai.tools import BaseTool
from src.config.settings import MONGO_URI, MAX_CVS

class CVFetcher(BaseTool):
    name: str = "CV Fetcher"
    description: str = "Fetches CVs of applicants based on job offer ID and extracts text from PDFs."

    def _run(self, offer_id: str):
        client = MongoClient(MONGO_URI)
        db = client['recrutement']
        fs = gridfs.GridFS(db)

        # Ne récupérer que les postulations non traitées
        postulations = list(db['postulation'].find({
            "id_offre": ObjectId(offer_id),
            "traite": False
        }))
        candidate_ids = [p["id_candidat"] for p in postulations]

        # Récupérer les candidats correspondants
        candidates = db['candidat'].find({"_id": {"$in": candidate_ids}})

        results = []
        for c in candidates:
            cv_id = c.get("cv_file_id")
            if not cv_id:
                continue
            try:
                file = fs.get(ObjectId(cv_id))
                text = self._extract_text(file.read())
                results.append({
                    "candidate_id": str(c["_id"]),
                    "filename": file.filename,
                    "text": text
                })
            except Exception as e:
                results.append({
                    "candidate_id": str(c["_id"]),
                    "filename": str(cv_id),
                    "error": str(e)
                })

        return results[:MAX_CVS]

    def _extract_text(self, pdf_bytes):
        text = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
