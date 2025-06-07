from crewai import Agent, Task, Crew
from agents.quiz_generator_agent import QuizGeneratorAgent
from agents.form_distribution_agent import FormDistributionAgent
from typing import List, Dict
import json
from src.config.llm_config import llm  # Import the Gemini LLM configuration

class TechnicalAssessmentCrew:
    def __init__(self, job_id: str, skills: List[str], num_candidates: int = 10):
        self.job_id = job_id
        self.skills = skills
        self.num_candidates = num_candidates
        
    def create_agents(self):
        # Quiz Generator Agent
        quiz_generator = Agent(
            name="Quiz Generator",
            role="Technical Quiz Expert",
            goal="Generate comprehensive technical assessment quizzes",
            backstory="""You are an expert in creating technical assessment quizzes.
            You understand various programming languages and frameworks, and can create
            challenging yet fair questions to evaluate candidates.""",
            agent_type=QuizGeneratorAgent,
            llm=llm  # Use Gemini LLM
        )

        # Form Distribution Agent
        form_distributor = Agent(
            name="Form Distributor",
            role="Assessment Distribution Expert",
            goal="Create and distribute assessment forms efficiently",
            backstory="""You are responsible for creating Google Forms from quiz content
            and ensuring they are distributed to the right candidates.""",
            agent_type=FormDistributionAgent,
            llm=llm  # Use Gemini LLM
        )

        return quiz_generator, form_distributor

    def create_tasks(self, quiz_generator: Agent, form_distributor: Agent):
        # Task 1: Generate Quiz
        generate_quiz = Task(
            description=f"""Generate a technical assessment quiz for job ID {self.job_id}.
            Include questions for the following skills: {', '.join(self.skills)}.
            Each skill should have multiple questions testing different aspects.""",
            agent=quiz_generator,
            expected_output="""A dictionary containing:
            {
                "job_id": "string",
                "offer_title": "string",
                "quiz": {
                    "skill_name": [
                        {
                            "Question": "string",
                            "A": "string",
                            "B": "string",
                            "C": "string",
                            "D": "string",
                            "Answer": "string"
                        }
                    ]
                }
            }"""
        )

        # Task 2: Create and Distribute Form
        distribute_form = Task(
            description="""Create a Google Form using the generated quiz and distribute
            it to the top candidates. Track the distribution status and return the results.""",
            agent=form_distributor,
            expected_output="""A dictionary containing:
            {
                "form_url": "string",
                "emails_sent": ["string"],
                "status": {"email": "status"}
            }""",
            dependencies=[generate_quiz]
        )

        return [generate_quiz, distribute_form]

    def run(self):
        try:
            # Create agents
            quiz_generator, form_distributor = self.create_agents()

            # Create tasks
            tasks = self.create_tasks(quiz_generator, form_distributor)

            # Create and run the crew
            crew = Crew(
                agents=[quiz_generator, form_distributor],
                tasks=tasks,
                verbose=True
            )

            result = crew.kickoff()

            # Process and return results
            return {
                "job_id": self.job_id,
                "skills_assessed": self.skills,
                "num_candidates": self.num_candidates,
                "assessment_results": result
            }

        except Exception as e:
            print(f"Error in crew workflow: {str(e)}")
            return {
                "error": str(e),
                "job_id": self.job_id,
                "status": "failed"
            }

def main():
    # Example usage
    job_id = "68245d91b285ae9b4f846cd9"  # Java Backend Developer position
    skills = ["spring boot", "java core", "rest api", "jpa"]
    num_candidates = 10

    # Create and run the crew
    crew = TechnicalAssessmentCrew(job_id, skills, num_candidates)
    result = crew.run()

    # Convert CrewOutput to dictionary
    if hasattr(result.get('assessment_results'), 'dict'):
        result['assessment_results'] = result['assessment_results'].dict()

    # Print results
    print("\nWorkflow Results:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 