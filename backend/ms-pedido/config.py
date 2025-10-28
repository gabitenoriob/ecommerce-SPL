from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # O Pydantic vai ler a variável de ambiente 'DATABASE_URL'
    # que será injetada pelo docker-compose.yml
    database_url: str = os.environ.get("DATABASE_URL")

# Instância única que será usada em todo o app
settings = Settings()