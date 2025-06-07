"""
Enhanced Form Distribution Task with better CrewAI compliance
"""

from crewai import Task
from src.agents.enhanced_form_distributor_agent import enhanced_form_distributor_agent
from src.tools.form.enhanced_google_form_creator import EnhancedGoogleFormCreator
from src.tools.form.enhanced_email_sender import EnhancedEmailSender
from src.config.settings import OUTPUT_QUIZ_DIR, CANDIDATES_NUMBER
import os

enhanced_form_distribution_task = Task(
    description=f"""
    Execute comprehensive technical assessment distribution workflow for top candidates.

    WORKFLOW STEPS:

    1. DATA PREPARATION:
       - Read quiz data from previous task output (quiz generation results)
       - Read candidate ranking data from ranking task output
       - Validate data integrity and completeness
       - Select top {CANDIDATES_NUMBER} candidates based on ranking scores

    2. GOOGLE FORM CREATION:
       - Use EnhancedGoogleFormCreator tool to create professional assessment form
       - Include all quiz questions with proper formatting
       - Set up form with clear instructions and professional appearance
       - Ensure form is accessible and properly configured
       - Obtain shareable form URL

    3. EMAIL DISTRIBUTION:
       - Use EnhancedEmailSender tool for candidate communication
       - Send personalized emails to top {CANDIDATES_NUMBER} candidates
       - Include form URL, assessment instructions, and deadline information
       - Track email delivery status for each candidate
       - Handle any delivery failures gracefully

    4. RESULTS COMPILATION:
       - Compile comprehensive distribution report
       - Include form URL, successful email deliveries, and any failures
       - Provide detailed status for recruitment team review

    INPUT REQUIREMENTS:
    - Quiz data with questions, options, and correct answers
    - Ranked candidate list with contact information
    - Job offer details for personalization

    OUTPUT REQUIREMENTS:
    - Google Form URL for the technical assessment
    - List of candidates who successfully received the assessment
    - Detailed delivery status report
    - Any error messages or failed deliveries

    QUALITY STANDARDS:
    - Professional email communication
    - Accurate form creation with all questions
    - Comprehensive error handling
    - Detailed tracking and reporting
    """,
    
    agent=enhanced_form_distributor_agent,
    
    tools=[
        EnhancedGoogleFormCreator(),
        EnhancedEmailSender()
    ],
    
    expected_output="""
    A comprehensive JSON report containing:
    {
        "form_creation": {
            "form_url": "https://docs.google.com/forms/d/[form_id]/viewform",
            "status": "success|failed",
            "questions_count": number,
            "creation_timestamp": "ISO timestamp"
        },
        "email_distribution": {
            "total_candidates": number,
            "emails_sent": number,
            "emails_failed": number,
            "successful_recipients": ["email1@domain.com", ...],
            "failed_recipients": [{"email": "email@domain.com", "error": "reason"}, ...],
            "distribution_timestamp": "ISO timestamp"
        },
        "summary": {
            "workflow_status": "completed|failed",
            "top_candidates_selected": number,
            "assessment_ready": boolean,
            "next_steps": "description of follow-up actions"
        }
    }
    """,
    
    output_file=os.path.join(OUTPUT_QUIZ_DIR, "enhanced_form_distribution_results.json")
)