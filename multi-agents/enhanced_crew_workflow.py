"""
Enhanced CrewAI-Compliant Multi-Agent Recruitment System
"""

import os
import json
import agentops
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configurations and components
from src.config.llm_config import llm
from src.agents import (
    job_offer_agent,
    cv_analysis_agent, 
    cv_ranker_agent,
    quiz_generator_agent,
    form_distributor_agent
)
from src.tasks import (
    job_offer_task,
    cv_task,
    rank_task,
    quiz_task,
    form_distribution_task
)

class EnhancedRecruitmentCrew:
    """
    Enhanced CrewAI-compliant recruitment automation system.
    
    This class orchestrates a multi-agent workflow for:
    1. Job offer processing and entity extraction
    2. CV analysis and candidate evaluation
    3. Candidate ranking and scoring
    4. Technical quiz generation using RAG
    5. Assessment distribution via Google Forms
    """
    
    def __init__(self, enable_agentops: bool = True):
        """Initialize the enhanced recruitment crew."""
        self.enable_agentops = enable_agentops
        
        if self.enable_agentops and os.getenv("AGENTOPS_API_KEY"):
            agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))
        
        # Validate environment configuration
        self._validate_environment()
        
        # Initialize crew components
        self.agents = self._get_agents()
        self.tasks = self._get_tasks()
        self.crew = self._create_crew()
    
    def _validate_environment(self) -> None:
        """Validate that all required environment variables are set."""
        required_vars = [
            "GEMINI_API_KEY",
            "MONGO_URI", 
            "QDRANT_URL",
            "CONTEXT_API_URL",
            "PREDICT_API_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    def _get_agents(self) -> List[Agent]:
        """Get all configured agents."""
        return [
            job_offer_agent,
            cv_analysis_agent,
            cv_ranker_agent, 
            quiz_generator_agent,
            form_distributor_agent
        ]
    
    def _get_tasks(self) -> List[Task]:
        """Get all configured tasks with proper dependencies."""
        # Set up task dependencies
        cv_task.context = [job_offer_task]
        rank_task.context = [job_offer_task, cv_task]
        quiz_task.context = [job_offer_task]
        form_distribution_task.context = [quiz_task, rank_task]
        
        return [
            job_offer_task,
            cv_task,
            rank_task,
            quiz_task,
            form_distribution_task
        ]
    
    def _create_crew(self) -> Crew:
        """Create and configure the CrewAI crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "huggingface",
                "config": {
                    "model": os.getenv("EMBEDDING_MODEL_NAME", "OrdalieTech/Solon-embeddings-large-0.1")
                }
            }
        )
    
    def execute_workflow(self) -> Dict[str, Any]:
        """
        Execute the complete recruitment workflow.
        
        Returns:
            Dict containing the results of all workflow steps
        """
        try:
            print("🚀 Starting Enhanced CrewAI Recruitment Workflow...")
            
            # Execute the crew workflow
            result = self.crew.kickoff()
            
            # Process and structure the results
            workflow_results = self._process_results(result)
            
            print("✅ Workflow completed successfully!")
            return workflow_results
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            if self.enable_agentops:
                agentops.end_session("Failed")
            raise
        finally:
            if self.enable_agentops:
                agentops.end_session("Success")
    
    def _process_results(self, crew_output) -> Dict[str, Any]:
        """Process and structure the crew execution results."""
        results = {
            "workflow_status": "completed",
            "timestamp": crew_output.timestamp if hasattr(crew_output, 'timestamp') else None,
            "tasks_completed": len(self.tasks),
            "agents_involved": len(self.agents)
        }
        
        # Try to extract individual task results
        if hasattr(crew_output, 'tasks_output'):
            task_results = {}
            for i, task_output in enumerate(crew_output.tasks_output):
                task_name = self.tasks[i].description.split('\n')[0][:50] + "..."
                task_results[f"task_{i+1}_{task_name}"] = {
                    "status": "completed",
                    "output": str(task_output)
                }
            results["task_results"] = task_results
        
        return results
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow."""
        return {
            "agents_count": len(self.agents),
            "tasks_count": len(self.tasks),
            "process_type": "sequential",
            "memory_enabled": True,
            "agentops_enabled": self.enable_agentops
        }

def main():
    """Main execution function."""
    try:
        # Initialize the enhanced crew
        recruitment_crew = EnhancedRecruitmentCrew(enable_agentops=True)
        
        # Display workflow status
        status = recruitment_crew.get_workflow_status()
        print("📊 Workflow Configuration:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Execute the workflow
        results = recruitment_crew.execute_workflow()
        
        # Save results to file
        output_file = "data/workflow_results.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Results saved to: {output_file}")
        
        return results
        
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    results = main()
    print("\n🎯 Workflow Summary:")
    print(json.dumps(results, indent=2))