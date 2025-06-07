# Diagramme de Composants du Système Multi-Agents

Ce répertoire contient le diagramme de composants UML qui décrit l'architecture complète du système multi-agents.

## Structure du Diagramme

Le diagramme illustre les éléments suivants :

### Composants Principaux
- **Crew Workflow Manager** : Gère le flux de travail global du système
- **Agent Operations** : Gère les opérations et la journalisation des agents
- **Agent Manager** : Contrôle et coordonne les agents individuels
- **Individual Agents** : Les agents qui effectuent les tâches spécifiques

### Gestion des Données
- **CV Data** : Données relatives aux CV
- **Quiz Data** : Données relatives aux quiz
- **Offer Data** : Données relatives aux offres
- **Classification Data** : Données de classification

### Code Source
- **Core Components** : Composants principaux du système
- **Test Components** : Composants de test

## Comment Visualiser le Diagramme

Le diagramme est écrit en PlantUML. Pour le visualiser, vous pouvez :

1. Utiliser un éditeur en ligne comme [PlantUML Web Server](https://www.plantuml.com/plantuml/uml/)
2. Installer un plugin PlantUML dans votre IDE
3. Utiliser l'outil en ligne de commande PlantUML

### Installation de PlantUML

1. Assurez-vous d'avoir Java installé sur votre système
2. Téléchargez PlantUML depuis [plantuml.com](https://plantuml.com/download)
3. Pour générer le diagramme en PNG :
   ```bash
   java -jar plantuml.jar component_diagram.puml
   ```

## Légende des Couleurs

- 🔵 **Bleu clair** : Composants principaux (Core)
- 🟢 **Vert clair** : Composants de données (Data)
- 🟡 **Jaune clair** : Composants des agents (Agent) 