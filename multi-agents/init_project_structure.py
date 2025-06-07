# init_project_structure.py

import os

structure = {
    "data": [],
    "src": [
        "config",
        "agents",
        "tasks",
        "tools/quiz",
        "crew",
        "utils"
    ],
    "apis": [
        "job_offer_ner_api",
        "quiz_context_api"
    ]
}

files = {
    ".env": "",
    "requirements.txt": "",
    "run.py": "# Point d’entrée (lance l’agent CrewAI)",
    "data/generated_quiz4.json": "{}",
    "src/config/settings.py": "# config settings",
    "src/agents/job_offer_agent.py": "# définition de l'agent",
    "src/tasks/generate_quiz_task.py": "# définition de la tâche",
    "src/tools/quiz/mongodb_offer_tool.py": "# outil MongoDB",
    "src/tools/quiz/entity_extractor_tool.py": "# outil d'extraction",
    "src/tools/quiz/quiz_generator_tool.py": "# outil de génération de quiz",
    "src/crew/crew_initializer.py": "# initialise le crew",
    "src/utils/io_helpers.py": "# fonctions utilitaires",
    "apis/job_offer_ner_api/app.py": "# API d'extraction",
    "apis/job_offer_ner_api/model_loader.py": "# chargement modèle",
    "apis/quiz_context_api/app.py": "# API de quiz contextuel",
}

def create_structure():
    for folder, subfolders in structure.items():
        os.makedirs(folder, exist_ok=True)
        for sub in subfolders:
            os.makedirs(os.path.join(folder, sub), exist_ok=True)

    for file_path, content in files.items():
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    create_structure()
    print("Structure du projet créée avec succès.")
