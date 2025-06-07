from crewai import Agent
from src.config.llm_config import llm 
from src.tools.quiz_generator_tool import QuizGenerationTool



quiz_generator_agent = Agent(
    llm=llm,
    role="Quiz Generator Based on Hard Skills",
    goal=(
        "Generate high-quality and well-structured multiple-choice quiz questions based on the extracted hard skills"
        "by using the quiz generator tool. "
    ),
    backstory=(
        "You are a recruitment automation assistant. You are responsible for transforming job offers "
        "into structured data and creating high-quality quizzes to evaluate candidates' technical knowledge. "
        "You use dedicated tools to fetch job offers, extract entities (like hard skills), "
        "retrieve relevant quiz contexts (sample questions), and generate the final quiz from that context."
    ),
    tools=[
        QuizGenerationTool()
    ],
    allow_delegation=True,
    verbose=True
)



