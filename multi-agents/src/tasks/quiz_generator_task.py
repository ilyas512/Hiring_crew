from crewai import Task
from src.agents.quiz_generator_agent import quiz_generator_agent
from src.config import settings
import os

quiz_task = Task(
    description=(
        "You are provided with a list of hard skills extracted from a job offer.\n"
        "Your job is to generate multiple-choice questions (MCQs) to assess candidates' knowledge of these skills.\n\n"

        "Step-by-step Instructions:\n"
        "1. Use the Quiz Generator Tool to retrieve *raw quiz context* for each hard skill.\n"
        "2. Based on that context, produce exactly {settings.NUM_QUIZ_QUESTIONS} MCQs.\n"
        "   - Reformulate questions from the context or create new good ones inspired by it.\n"
        "- Do NOT refer to 'code', 'examples', or 'provided context' unless actual code or examples are explicitly included.\n"
        "- Avoid vague phrases like 'Based on the following...' or 'According to the above...' unless there is actual content to reference.\n"
        "   - Do NOT invent content outside of what is supported by the context.\n\n"
        "   -  IMPORTANT: Do NOT generate questions that refer to code behavior, output, compilation, or execution unless the *full source code* is clearly available in the context.\n" 
        " Avoid questions like 'What will be the output of the following Java program?' if the code is not shown."
        " Avoid questions like 'What will be the output of the following Java program?' unless the full source code is included in the context, and you explicitly include the code in the question.\n" 
        "If the context contains code, you must paste it inside the question before asking about its output.\n" 
        "You must NEVER assume a code snippet is known by the candidate. You must show it in the question if it’s necessary to answer.\n" 
        "All code snippets must be properly formatted."
        "Never insert code with escaped characters like \\n, \\t, etc. Use clean multiline formatting."
       
        "Formatting Rules:\n"
        "- Group the questions under their corresponding hard skill.\n"
        "- Each question must have this format:\n"
        "  Question:\n"
        "  <Your question>\n"
        "  A. <Option A>\n"
        "  B. <Option B>\n"
        "  C. <Option C>\n"
        "  D. <Option D>\n"
        "  Answer: <Correct Option Letter>\n"
        "- Ensure exactly 4 options per question, and only one correct answer.\n"
        "- Tailor each question to the required difficulty level: *'{settings.QUIZ_LEVEL}'*.\n\n"

        "Final Output Format:\n"
        "Return a clean JSON object with:\n"
        "- 'offer_id'\n"
        "- 'offer_title'\n"
        "- 'hard_skills': list of hard skills used\n"
        "- 'quiz': dictionary where each key is a hard skill and its value is a list of MCQs\n\n"

        " Strict Constraints:\n"
        "- Exactly {settings.NUM_QUIZ_QUESTIONS} questions in total\n"
        "- Follow the format strictly\n"
        "- Do not include raw context in the final output\n"
        " - Do NOT generate a question if essential information (like code snippet) is missing. Skip it.\n"
        "- Do not invent questions or answers\n"
    ),
    agent=quiz_generator_agent,
    expected_output=(
    "A JSON object with:\n"
    "- 'offer_id'\n"
    "- 'offer_title'\n"
    "- 'hard_skills': list of skills used\n"
    "- 'quiz': dictionary where each key is a hard skill and its value is a list of MCQs\n"
    f"The quiz must contain exactly {settings.NUM_QUIZ_QUESTIONS} questions total, grouped by skill, and follow the required format."
    ),
    output_file=os.path.join(settings.OUTPUT_QUIZ_DIR, "quiz_from_hard_skills3.json")
)
