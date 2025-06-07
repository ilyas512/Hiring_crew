from crewai import Task
from src.agents.form_distributor_agent import form_distributor_agent
from src.tools.form.google_form_creator import GoogleFormCreator
from src.tools.form.email_sender import EmailSender
from src.config.settings import OUTPUT_QUIZ_DIR, CANDIDATES_NUMBER
import os

form_distribution_task = Task(
    description=f"""
    Create and distribute technical assessment forms to top candidates.

    Steps:
    1. Read the quiz data from the quiz generation output
    2. Create a Google Form with the quiz questions
    3. Send the form to the top {CANDIDATES_NUMBER} candidates based on their ranking

    Input Format:
    - Quiz data JSON with questions and options
    - Ranked candidates list with emails

    Required Actions:
    1. Use GoogleFormCreator tool to:
       - Create a new form with the quiz title and description
       - Add all questions with their options
       - Get the form URL

    2. Use EmailSender tool to:
       - Send emails to top {CANDIDATES_NUMBER} candidates
       - Include form URL and instructions
       - Track successful sends

    Output Format:
    JSON object containing:
    - 'form_url': URL of created Google Form
    - 'emails_sent': List of candidates who received the assessment
    - 'status': Success/failure status for each email sent
    """,
    agent=form_distributor_agent,
    tools=[
        GoogleFormCreator(),
        EmailSender()
    ],
    output_file=os.path.join(OUTPUT_QUIZ_DIR, "form_distribution_results.json"),
    expected_output="""A JSON string containing the Google Form URL and email distribution results, formatted as:
    {
        "form_url": "https://docs.google.com/forms/d/...",
        "emails_sent": ["candidate1@email.com", "candidate2@email.com", ...],
        "status": {
            "candidate1@email.com": "success",
            "candidate2@email.com": "success",
            ...
        }
    }"""
) 