from crewai import Agent
from src.config.llm_config import llm
from src.tools.cv_fetcher_tool import CVFetcher
from src.tools.cv_entity_extractor import CVEntityExtractor

cv_analysis_agent = Agent(
    llm=llm,
    role="CV Analysis Agent",
    goal=(
        "Retrieve the resumes (CVs) of candidates who applied to a given job offer, "
        "extract their content, and identify entities (technical skills, etc.)."
    ),
    backstory=(
        "As a specialist in automated resume processing, you use MongoDB GridFS to read PDF files, "
        "and extract useful data via an entity extraction API."
    ),
    tools=[
        CVFetcher(),
        CVEntityExtractor()
    ],
    allow_delegation=False,
    verbose=True
)

