from crewai import Task
from src.agents.cv_analysis_agent import cv_analysis_agent
from src.tools.cv_fetcher_tool import CVFetcher
from src.tools.cv_entity_extractor import CVEntityExtractor
from src.config.settings import OUTPUT_CV_DIR
from src.config.settings import MAX_CVS
import os

cv_task = Task(
    description=(
        f"This task involves preparing structured data from applicant CVs for a given job offer.\n\n"
        
        "STEP 1: Retrieve CVs Based on Job Offer ID\n"
        "- Use the `CVFetcher` tool with the provided `job_offer_id`.\n"
        "- This tool retrieves all unprocessed applications for the offer, extracts the corresponding CV PDFs from the database, and extracts raw text from them.\n"
        f"- Limit processing to the first {MAX_CVS} CVs.\n\n"

        "STEP 2: Extract Structured Information From CV Text\n"
        "- Use the `CVEntityExtractor` tool to convert each CV's raw text into structured fields.\n"
        "- Required fields per candidate: `FNAME`, `LNAME`, `EMAIL`, `HSKILL`, `SSKILL`, `EXPERIENCE`, `EDUCATION`.\n"
        "- Normalize the skill fields: lowercase, split multi-skill strings, deduplicate entries.\n\n"

        "STEP 3: Generate Final Output\n"
        "Final Output Format (JSON):\n"
        "- 'offer_id': job offer ID\n"
        "- 'offer_title': job title\n"
        "- 'applicants': list of applicants structred data using CV entity extractor tool (as strings)\n"
        "- 'entities': normalized fields including hard_skills, soft_skills, experience, and education."
    ),
     expected_output=(
        "Final Output Format (JSON):\n"
        "- 'offer_id': job offer ID\n"
        "- 'offer_title': job title\n"
        "- 'applicants': list of applicants structred data using CV entity extractor tool (as strings)\n"
        "- 'entities': normalized fields including hard_skills, soft_skills, experience, and education."
        
    ),
    agent=cv_analysis_agent,
    tools=[
        CVFetcher(),
        CVEntityExtractor()
    ],
    output_file=os.path.join(OUTPUT_CV_DIR, "CV_extracted_entities3.json")   
)


