from crewai import Agent
from src.config.llm_config import llm
from src.tools.job_offer_fetcher_tool import JobOfferFetcher
from src.tools.job_offer_entity_extractor import JobOfferEntityExtractor

job_offer_agent = Agent(
    llm=llm,
    role="Job Offer Processing Agent",
    goal=(
        "Retrieve the latest job offer from the databas "
        "and extract key structured entities."
    ),
    backstory=(
        "You are a recruitment automation assistant. You are responsible for transforming job offers "
        "into structured data by using dedicated tools to fetch job offers and extract entities"
    ),
    tools=[
        JobOfferFetcher(),
        JobOfferEntityExtractor()
    ],
    allow_delegation=False,
    verbose=True
)
