"""
Enhanced Form Distribution Agent with improved CrewAI compliance
"""

from crewai import Agent
from src.config.llm_config import llm
from src.tools.form.enhanced_google_form_creator import EnhancedGoogleFormCreator
from src.tools.form.enhanced_email_sender import EnhancedEmailSender

enhanced_form_distributor_agent = Agent(
    role='Enhanced Form Distribution Specialist',
    goal="""Create professional Google Forms for technical assessments and distribute them 
    efficiently to top-ranked candidates via personalized emails with comprehensive tracking.""",
    
    backstory="""You are an expert in recruitment automation and candidate communication. 
    Your responsibility is to transform technical quiz data into professional Google Forms 
    and ensure seamless distribution to qualified candidates. You maintain high standards 
    for professional communication and track all interactions for recruitment analytics.""",
    
    llm=llm,
    tools=[
        EnhancedGoogleFormCreator(),
        EnhancedEmailSender()
    ],
    allow_delegation=False,
    verbose=True,
    max_iter=3,
    memory=True
)