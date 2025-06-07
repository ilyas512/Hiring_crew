import requests

url = "http://127.0.0.1:5001/get_contexts"

data = {
    "hard_skills": [
        "java", "spring boot", "jpa", "hibernate", "rest api", "postgresql",
        "mysql", "mongodb", "maven", "gradle", "git", "ci/cd", "docker",
        "kubernetes", "aws", "gcp", "kafka", "rabbitmq", "elk stack",
        "prometheus", "grafana"
    ]
}

response = requests.post(url, json=data)

print("Status code:", response.status_code)
print("Raw response text:")
print(response.text)

# Essayer le JSON seulement si le code est 200
if response.status_code == 200:
    print("Parsed JSON:", response.json())
