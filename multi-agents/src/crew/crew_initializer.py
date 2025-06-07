from crewai import Crew, Process
from src.agents.job_offer_agent import job_offer_agent
from src.agents.cv_analysis_agent import cv_analysis_agent
from src.agents.cv_ranker_agent import cv_ranker_agent
from src.agents.quiz_generator_agent import quiz_generator_agent
from src.agents.form_distributor_agent import form_distributor_agent
from src.tasks.job_offer_task import job_offer_task
from src.tasks.cv_task import cv_task
from src.tasks.rank_task import rank_task
from src.tasks.quiz_generator_task import quiz_task
from src.tasks.form_distribution_task import form_distribution_task


crew = Crew(
    agents=[
        job_offer_agent,
        cv_analysis_agent,
        cv_ranker_agent,
        quiz_generator_agent,
        form_distributor_agent
    ],
    tasks=[
        job_offer_task,
        cv_task,
        rank_task,
        quiz_task,
        form_distribution_task
    ],
    process=Process.sequential,
)


