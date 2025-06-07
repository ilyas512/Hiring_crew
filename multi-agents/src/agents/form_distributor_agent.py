from crewai import Agent
from src.config.llm_config import llm
from src.tools.form.google_form_creator import GoogleFormCreator
from src.tools.form.email_sender import EmailSender

form_distributor_agent = Agent(
    role='Form Distribution Agent',
    goal='Create Google Forms for technical assessments and distribute them to top candidates via email',
    backstory="""You are responsible for creating Google Forms from quiz questions and sending them to candidates.
    You ensure that only the top candidates receive the assessment and that the forms are properly formatted.""",
    llm=llm,
    tools=[
        GoogleFormCreator(),
        EmailSender()
    ],
    allow_delegation=False,
    verbose=True
) 