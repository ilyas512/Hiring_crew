import requests
from crewai.tools import BaseTool

class CVEntityExtractor(BaseTool):
    name: str = "CV Entity Extractor"
    description: str = "Extract structured entities (skills, experience, education) from CV text."

    def _run(self, cv_data: list):
        if not isinstance(cv_data, list) or not all("text" in entry for entry in cv_data):
            raise ValueError("Input must be a list of dictionaries with 'text' keys.")

        texts = [entry["text"] for entry in cv_data]

        try:
            response = requests.post("http://127.0.0.1:5004/extract-info/", json={"texts": texts})
            response.raise_for_status()
            extracted_info = response.json().get("extracted_info", [])
        except Exception as e:
            raise RuntimeError(f"Error contacting CV entity API: {e}")

        def normalize(skills):
            return list(set(skill.strip().lower() for group in skills for skill in group.split()))

        results = []
        for original, extracted in zip(cv_data, extracted_info):
            if 'HSKILL' in extracted:
                extracted['HSKILL'] = normalize(extracted['HSKILL'])
            if 'SSKILL' in extracted:
                extracted['SSKILL'] = normalize(extracted['SSKILL'])

            results.append({
                "candidate_id": original.get("candidate_id"),
                "entities": extracted
            })

        print("CVs - Entités extraites:", results)
        return results
