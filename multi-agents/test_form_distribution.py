from agents.form_distribution_agent import FormDistributionAgent

def main():
    # Sample quiz data
    quiz_data = {
        "offer_title": "Java Backend Developer",
        "quiz": {
            "spring boot": [
                {
                    "Question": "What role does Spring Boot DevTools play?",
                    "A": "Improving build speed",
                    "B": "Automatic restart",
                    "C": "Code generation",
                    "D": "Dependency management",
                    "Answer": "B"
                }
            ],
            "java core": [
                {
                    "Question": "What is the purpose of the `synchronized` keyword in Java?",
                    "A": "To create JavaBeans",
                    "B": "To execute SQL queries",
                    "C": "To create a synchronized block of code for multithreading",
                    "D": "To define JavaBean properties",
                    "Answer": "C"
                }
            ]
        }
    }

    # Create form distribution agent
    agent = FormDistributionAgent()

    try:
        # Test form creation only (without email distribution)
        print("Creating Google Form...")
        result = agent.create_and_distribute_forms(quiz_data, candidate_emails=[])
        
        # Print results
        print(f"\nForm URL: {result['form_url']}")
        
        if result['form_url']:
            print("\nForm created successfully!")
            print("You can now manually test the form by opening the URL in a browser.")
        else:
            print("\nError: Form creation failed.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 