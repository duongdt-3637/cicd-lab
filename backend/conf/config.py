import os

APP_NAME = "cicd-lab"
RUNTIME_ENV = os.environ.get("RUNTIME_ENV", "local")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Lấy từ Secrets Manager `cicd-lab/<env>` qua template.yaml ({{resolve:secretsmanager:...}})
APP_MESSAGE = os.environ.get("APP_MESSAGE", "Hello (no secret)")
