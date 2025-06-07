import requests
from crewai.tools import BaseTool
from typing import Dict, Any
from src.config import settings

class QuizGenerationTool(BaseTool):
    name: str = "Quiz Generator"
    description: str = (
        "Generates context for each hard skill using a Flask API. "
        "Expects input_data to include either 'hard_skills' directly, or under job_offer.entities."
    )

    def _run(self, input_data: Dict[str, Any]):
        hard_skills = None

        # Cas 1 : input_data["hard_skills"]
        if isinstance(input_data, dict) and "hard_skills" in input_data:
            hard_skills = input_data["hard_skills"]

        # Cas 2 : input_data["job_offer"]["entities"]["hard_skills"]
        elif isinstance(input_data, dict):
            try:
                hard_skills = input_data["job_offer"]["entities"]["hard_skills"]
            except (KeyError, TypeError):
                pass

        if not isinstance(hard_skills, list) or not all(isinstance(s, str) for s in hard_skills):
            return {"error": "Missing or invalid 'hard_skills' field. Must be a list of strings."}

        # Optionnel : limiter pour la rapidité
        limited_hard_skills = hard_skills[:5]

        url = settings.CONTEXT_API_URL  # ex: http://localhost:5001/get_contexts

        try:
            response = requests.post(url, json={"hard_skills": limited_hard_skills})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
