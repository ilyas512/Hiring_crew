"""
CrewAI System Validation Script
Validates the enhanced multi-agent system for CrewAI compliance
"""

import os
import json
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration."""
    print("🔍 Validating Environment Configuration...")
    
    required_vars = {
        "GEMINI_API_KEY": "Gemini API key for LLM",
        "MONGO_URI": "MongoDB connection string",
        "QDRANT_URL": "Qdrant vector database URL",
        "CONTEXT_API_URL": "Quiz context API endpoint",
        "PREDICT_API_URL": "NER prediction API endpoint"
    }
    
    optional_vars = {
        "AGENTOPS_API_KEY": "AgentOps monitoring (optional)",
        "GOOGLE_CREDENTIALS_PATH": "Google API credentials",
        "SMTP_USERNAME": "Email configuration",
        "SMTP_PASSWORD": "Email configuration"
    }
    
    results = {
        "required": {},
        "optional": {},
        "status": "passed"
    }
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        results["required"][var] = {
            "present": bool(value),
            "description": description,
            "value_preview": value[:10] + "..." if value and len(value) > 10 else value
        }
        if not value:
            results["status"] = "failed"
            print(f"❌ Missing required variable: {var}")
        else:
            print(f"✅ {var}: Present")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        results["optional"][var] = {
            "present": bool(value),
            "description": description
        }
        status = "✅" if value else "⚠️"
        print(f"{status} {var}: {'Present' if value else 'Not set (optional)'}")
    
    return results

def validate_agents() -> Dict[str, Any]:
    """Validate agent configurations."""
    print("\n🤖 Validating Agent Configurations...")
    
    try:
        from src.agents import (
            job_offer_agent,
            cv_analysis_agent,
            cv_ranker_agent,
            quiz_generator_agent,
            form_distributor_agent
        )
        
        agents = [
            ("Job Offer Agent", job_offer_agent),
            ("CV Analysis Agent", cv_analysis_agent),
            ("CV Ranker Agent", cv_ranker_agent),
            ("Quiz Generator Agent", quiz_generator_agent),
            ("Form Distributor Agent", form_distributor_agent)
        ]
        
        results = {"agents": {}, "status": "passed"}
        
        for name, agent in agents:
            agent_info = {
                "role": getattr(agent, 'role', 'Not defined'),
                "goal": getattr(agent, 'goal', 'Not defined'),
                "tools_count": len(getattr(agent, 'tools', [])),
                "llm_configured": hasattr(agent, 'llm') and agent.llm is not None
            }
            
            results["agents"][name] = agent_info
            
            if agent_info["llm_configured"]:
                print(f"✅ {name}: Properly configured")
            else:
                print(f"❌ {name}: Missing LLM configuration")
                results["status"] = "failed"
        
        return results
        
    except ImportError as e:
        print(f"❌ Failed to import agents: {str(e)}")
        return {"status": "failed", "error": str(e)}

def validate_tasks() -> Dict[str, Any]:
    """Validate task configurations."""
    print("\n📋 Validating Task Configurations...")
    
    try:
        from src.tasks import (
            job_offer_task,
            cv_task,
            rank_task,
            quiz_task,
            form_distribution_task
        )
        
        tasks = [
            ("Job Offer Task", job_offer_task),
            ("CV Analysis Task", cv_task),
            ("Ranking Task", rank_task),
            ("Quiz Generation Task", quiz_task),
            ("Form Distribution Task", form_distribution_task)
        ]
        
        results = {"tasks": {}, "status": "passed"}
        
        for name, task in tasks:
            task_info = {
                "description_length": len(getattr(task, 'description', '')),
                "has_agent": hasattr(task, 'agent') and task.agent is not None,
                "has_expected_output": hasattr(task, 'expected_output') and task.expected_output,
                "has_output_file": hasattr(task, 'output_file') and task.output_file,
                "tools_count": len(getattr(task, 'tools', []))
            }
            
            results["tasks"][name] = task_info
            
            if all([task_info["has_agent"], task_info["description_length"] > 0]):
                print(f"✅ {name}: Properly configured")
            else:
                print(f"❌ {name}: Missing required configuration")
                results["status"] = "failed"
        
        return results
        
    except ImportError as e:
        print(f"❌ Failed to import tasks: {str(e)}")
        return {"status": "failed", "error": str(e)}

def validate_tools() -> Dict[str, Any]:
    """Validate tool configurations."""
    print("\n🔧 Validating Tool Configurations...")
    
    try:
        from src.tools import (
            JobOfferFetcher,
            JobOfferEntityExtractor,
            CVFetcher,
            CVEntityExtractor,
            QuizGenerationTool,
            GoogleFormCreator,
            EmailSender
        )
        
        tools = [
            ("Job Offer Fetcher", JobOfferFetcher),
            ("Job Offer Entity Extractor", JobOfferEntityExtractor),
            ("CV Fetcher", CVFetcher),
            ("CV Entity Extractor", CVEntityExtractor),
            ("Quiz Generation Tool", QuizGenerationTool),
            ("Google Form Creator", GoogleFormCreator),
            ("Email Sender", EmailSender)
        ]
        
        results = {"tools": {}, "status": "passed"}
        
        for name, tool_class in tools:
            try:
                # Try to instantiate the tool
                tool_instance = tool_class()
                tool_info = {
                    "instantiable": True,
                    "has_name": hasattr(tool_instance, 'name'),
                    "has_description": hasattr(tool_instance, 'description'),
                    "has_run_method": hasattr(tool_instance, '_run')
                }
                
                results["tools"][name] = tool_info
                
                if all(tool_info.values()):
                    print(f"✅ {name}: Properly configured")
                else:
                    print(f"❌ {name}: Missing required attributes")
                    results["status"] = "failed"
                    
            except Exception as e:
                print(f"❌ {name}: Failed to instantiate - {str(e)}")
                results["tools"][name] = {"error": str(e)}
                results["status"] = "failed"
        
        return results
        
    except ImportError as e:
        print(f"❌ Failed to import tools: {str(e)}")
        return {"status": "failed", "error": str(e)}

def validate_directory_structure() -> Dict[str, Any]:
    """Validate project directory structure."""
    print("\n📁 Validating Directory Structure...")
    
    required_dirs = [
        "src/agents",
        "src/tasks", 
        "src/tools",
        "src/config",
        "data/quiz",
        "data/offer",
        "data/cv",
        "data/classif"
    ]
    
    results = {"directories": {}, "status": "passed"}
    
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        results["directories"][dir_path] = exists
        
        if exists:
            print(f"✅ {dir_path}: Exists")
        else:
            print(f"❌ {dir_path}: Missing")
            results["status"] = "failed"
    
    return results

def main():
    """Run complete system validation."""
    print("🚀 Starting CrewAI System Validation...\n")
    
    validation_results = {
        "timestamp": "2025-01-07",
        "environment": validate_environment(),
        "directory_structure": validate_directory_structure(),
        "agents": validate_agents(),
        "tasks": validate_tasks(),
        "tools": validate_tools()
    }
    
    # Overall status
    all_passed = all(
        result.get("status") == "passed" 
        for result in validation_results.values() 
        if isinstance(result, dict) and "status" in result
    )
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 VALIDATION PASSED: System is CrewAI-compliant!")
        validation_results["overall_status"] = "passed"
    else:
        print("❌ VALIDATION FAILED: Issues found that need attention")
        validation_results["overall_status"] = "failed"
    print(f"{'='*50}")
    
    # Save validation results
    os.makedirs("data", exist_ok=True)
    with open("data/validation_results.json", "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📊 Detailed results saved to: data/validation_results.json")
    
    return validation_results

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    if results["overall_status"] == "passed":
        sys.exit(0)
    else:
        sys.exit(1)