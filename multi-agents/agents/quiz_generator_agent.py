from typing import List, Dict, Any
from crewai.agent import Agent
import json
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()

class QuizGeneratorAgent(Agent):
    """Agent responsible for generating technical assessment quizzes using RAG."""

    def __init__(self):
        """Initialize the QuizGeneratorAgent with Qdrant and LLM."""
        super().__init__()
        
        # Initialize embeddings with Solon model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL_NAME", "OrdalieTech/Solon-embeddings-large-0.1"),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection_name = "technical_questions"
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Initialize question generation prompt
        self.question_prompt = PromptTemplate(
            input_variables=["skill", "context"],
            template="""Based on the following technical context about {skill}, generate a new multiple-choice question.
            
Context:
{context}

Generate a challenging technical question that:
1. Tests deep understanding of the concept
2. Has 4 options (A, B, C, D)
3. Has only one correct answer
4. Includes a brief explanation of why the answer is correct

Format the response as a JSON object with these fields:
- Question: the question text
- A: first option
- B: second option
- C: third option
- D: fourth option
- Answer: the correct option letter
- Explanation: why this answer is correct

Make sure the question is different from but inspired by the context."""
        )
        
        # Create the question generation chain
        self.question_chain = LLMChain(
            llm=self.llm,
            prompt=self.question_prompt
        )

    def get_context_for_skill(self, skill: str, num_docs: int = 3) -> str:
        """Retrieve relevant context from Qdrant for a given skill."""
        try:
            vector_store = Qdrant(
                client=self.qdrant_client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )

            # Get relevant documents
            results = vector_store.similarity_search(
                f"technical concepts and best practices in {skill}",
                k=num_docs,
                filter={"skill": skill}
            )

            # Combine context from documents
            context = "\n\n".join([
                f"Question: {doc.page_content}\n" +
                f"Options: A) {doc.metadata['options']['A']}, " +
                f"B) {doc.metadata['options']['B']}, " +
                f"C) {doc.metadata['options']['C']}, " +
                f"D) {doc.metadata['options']['D']}\n" +
                f"Answer: {doc.metadata['answer']}"
                for doc in results
            ])

            return context

        except Exception as e:
            print(f"Error getting context for {skill}: {str(e)}")
            return ""

    def generate_new_question(self, skill: str, context: str) -> Dict[str, Any]:
        """Generate a new question using LLM and RAG context."""
        try:
            # Generate question using the chain
            result = self.question_chain.run(skill=skill, context=context)
            
            # Parse the JSON response
            question_data = json.loads(result)
            return question_data

        except Exception as e:
            print(f"Error generating question for {skill}: {str(e)}")
            return None

    def generate_quiz(self, job_id: str, skills: List[str], questions_per_skill: int = 3) -> Dict[str, Any]:
        """Generate a quiz with new questions for each skill using RAG."""
        try:
            print(f"Generating quiz for job ID: {job_id}")
            print(f"Skills to assess: {', '.join(skills)}")
            
            quiz_data = {
                "job_id": job_id,
                "offer_title": "Java Backend Developer",  # This should be fetched based on job_id
                "quiz": {}
            }

            # Generate new questions for each skill
            for skill in skills:
                print(f"\nGenerating questions for {skill}...")
                skill_questions = []
                
                # Get context from Qdrant
                context = self.get_context_for_skill(skill)
                if not context:
                    print(f"Warning: No context available for skill: {skill}")
                    continue

                # Generate multiple questions
                for i in range(questions_per_skill):
                    question = self.generate_new_question(skill, context)
                    if question:
                        skill_questions.append(question)
                        print(f"Generated question {i+1}/{questions_per_skill} for {skill}")
                    else:
                        print(f"Failed to generate question {i+1} for {skill}")

                if skill_questions:
                    quiz_data["quiz"][skill] = skill_questions
                else:
                    print(f"Warning: No questions generated for skill: {skill}")

            return quiz_data

        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            return None

    def _run(self, task_description: str) -> Dict[str, Any]:
        """Required method from Agent class. Processes the task and returns results."""
        try:
            # Parse job ID and skills from task description
            lines = task_description.split('\n')
            job_id = lines[0].split('job ID ')[1].split('.')[0].strip()
            skills = [s.strip() for s in lines[1].split(':')[1].split(',')]

            # Generate the quiz using RAG
            quiz_data = self.generate_quiz(job_id, skills)
            
            if not quiz_data:
                raise Exception("Failed to generate quiz")

            return quiz_data

        except Exception as e:
            print(f"Error in quiz generation task: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            } 