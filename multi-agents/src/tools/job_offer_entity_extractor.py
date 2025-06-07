import requests
from crewai.tools import BaseTool

class JobOfferEntityExtractor(BaseTool):
    name: str = "Job Offer Entity Extractor"
    description: str = "Extract structured entities (skills, experience, education) from a job offer."

    def _run(self, input_data: dict):
        description = input_data.get("description")
        if not description:
            raise ValueError("Missing 'description' in input_data.")

        try:
            response = requests.post("http://127.0.0.1:5000/predict", json={"job_offer": description})
            response.raise_for_status()
            entities = response.json()
        except Exception as e:
            raise RuntimeError(f"Error contacting job offer entity API: {e}")

        # Validation
        required_fields = ["hard_skills", "soft_skills", "experience", "education"]

        # Vérifie que les clés sont bien là (même vides)
        missing_keys = [field for field in required_fields if field not in entities]
        if missing_keys:
            raise ValueError(f"Job offer entity extraction failed: missing keys {missing_keys}")


        print("Offres - Entités extraites:", entities)
        return entities
