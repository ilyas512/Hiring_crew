from crewai import Task
from src.agents.job_offer_agent import job_offer_agent
from src.tools.job_offer_fetcher_tool import JobOfferFetcher
from src.tools.job_offer_entity_extractor import JobOfferEntityExtractor
from src.config.settings import OUTPUT_OFFER_DIR
import os


job_offer_task = Task(
    description=(
        "Step 1: Use the 'Job Offer Fetcher' tool to retrieve the most recent job offer from the MongoDB database.\n"
        "- Extract and preserve the following fields from the offer document:\n"
        "  • 'id' (ObjectId as string)\n"
        "  • 'title' (string)\n"
        "  • 'description' (string)\n"
        "- This job offer ID will be reused in the next stages of the recruitment pipeline .\n\n"

        "Step 2: Use the 'Job Offer Entity Extractor' tool to extract structured information from the job description.\n"
        "- The API should return the following structured fields: 'hard_skills', 'soft_skills', 'experience', 'education'.\n"
        "- Ensure data normalization:\n"
        "  • Convert all skill/keyword values to lowercase.\n"
        "  • Remove duplicates and trim whitespace.\n"
        "- Absolutely no invented or hallucinated data should be added.\n"

        "Final Output Format (JSON):\n"
        "{\n"
        "  'offer_id': job offer ID,\n"
        "  'offer_title': job title,\n"
        "  'entities': {\n"
        "    'hard_skills': list of extracted hard skills,\n"
        "    'soft_skills': list of extracted soft skills,\n"
        "    'experience': extracted experience,\n"
        "    'education': extracted education\n"
        "  }\n"
        "}"
    ),
    expected_output=(
        "A well-structured JSON object with fields: id_offer, title, and a normalized 'entities' dictionary containing extracted job requirements."
    ),
    agent=job_offer_agent,
    tools=[
        JobOfferFetcher(),
        JobOfferEntityExtractor()
    ],
    output_file=os.path.join(OUTPUT_OFFER_DIR, "offer_extracted_entities3.json")
)
