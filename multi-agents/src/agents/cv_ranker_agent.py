from crewai import Agent
from src.config.llm_config import llm


cv_ranker_agent = Agent(
    role="CV Ranker",
    goal="Classify candidates into Tier 1, 2 or 3.",
    backstory="You use objective criteria to classify CVs based on extracted scores.",
    llm=llm,
    tools=[],
    verbose=True
)