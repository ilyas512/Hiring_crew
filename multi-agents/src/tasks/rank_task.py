from crewai import Task
from src.agents.cv_ranker_agent import cv_ranker_agent
from src.config.settings import OUTPUT_CLASSIF_DIR
import os


rank_task = Task(
    description = (
    " **Objective:**\n"
    "Rank up to N job applicants objectively and scientifically based on their alignment with a given job offer.\n\n"
    
    " **Input JSON Structure:**\n"
    "{\n"
    "  'id': <job_offer_id>,\n"
    "  'title': <job_title>,\n"
    "  'description': <job_description>,\n"
    "  'entities': {\n"
    "     'hard_skills': [...],\n"
    "     'soft_skills': [...],\n"
    "     'experience': [...],\n"
    "     'education': [...]\n"
    "  },\n"
    "  'applicants': [\n"
    "    {\n"
    "      'FNAME': <first_name>,\n"
    "      'LNAME': <last_name>,\n"
    "      'EMAIL': <email>,\n"
    "      'HSKILL': [...],\n"
    "      'SSKILL': [...],\n"
    "      'EXPERIENCE': [...],\n"
    "      'EDUCATION': [...]\n"
    "    },\n"
    "    ...\n"
    "  ]\n"
    "}\n\n"

    " **Scoring Guidelines (Strict Scientific Criteria):**\n"
    "For each applicant, assign points according to precise matching with job offer requirements:\n"
    "- **Hard Skills (0-3 points):**\n"
    "   - 3 = >=80% match | 2 = 50-79% match | 1 = 20-49% match | 0 = <20%\n"
    "- **Soft Skills (0-3 points):**\n"
    "   - Same thresholds as above\n"
    "- **Experience (0-3 points):**\n"
    "   - Based on direct relevance and duration alignment\n"
    "- **Education (0-3 points):**\n"
    "   - Based on level, field relevance, and requirement match\n"
    "- **Total Score:** Scaled to 0–100% using a weighted sum\n\n"

    " **Steps to Follow:**\n"
    "1. For each applicant, evaluate all 4 criteria based on overlap with `entities`.\n"
    "2. Compute the total score and convert to percentage.\n"
    "3. Assign a **tier**:\n"
    "   - Tier 1: 85–100%\n"
    "   - Tier 2: 70–84%\n"
    "   - Tier 3: 50–69%\n"
    "   - Tier 4: <50%\n"
    "4. Sort candidates in **descending order** of total score.\n\n"

    " **Expected Output (JSON Array):**\n"
    "A valid JSON object with two top-level keys:\n"
    "1. 'job_offer': containing:\n"
    "   - 'id': job offer ID (as provided)\n"
    "   - 'title': job title\n"
    "   - 'entities': structured offer entities (hard_skills, soft_skills, experience, education)\n"
    "\n"

    "2. 'candidates': an array **sorted in descending score**, each with:\n"
    "A list of candidates with the following fields for each:\n"
    "   - 'candidate_id': original ID\n"
    "- 'full_name': FNAME + ' ' + LNAME (preserve exactly as received)\n"
    "- 'email': as provided\n"
    "- 'score': percentage score (e.g. 78%)\n"
    "- 'tier': Tier 1–4\n"
    "- 'summary': brief justification of the score based on matched criteria\n\n"

    "⚠️ **Strict Rules:**\n"
    "- DO NOT invent or assume missing data.\n"
    "- DO NOT alter names, emails, or CV content.\n"
    "- DO NOT skip or filter any applicant.\n"
    "- The output must be a clean, valid JSON array — **no extra text or explanation**."
),

expected_output = (
    "A valid JSON object with two top-level keys:\n"
    "1. 'job_offer': an object containing:\n"
    "   - 'offer_id'\n"
    "   - 'offer_title'\n"
    "   - 'entities'\n"
    "\n"
    "2. 'candidates': a JSON array **sorted by descending score**, with each entry containing:\n"
    "   - 'candidate_id'\n"
    "   - 'full_name'\n"
    "   - 'email'\n"
    "   - 'score'\n"
    "   - 'tier'"
    "   - 'summary'\n"
    "\n"
    "Each candidate must appear exactly once, unmodified, and scored strictly according to the job offer criteria."
),

    agent=cv_ranker_agent,
    output_file=os.path.join(OUTPUT_CLASSIF_DIR, "candidate_scoring_results3.json")
)