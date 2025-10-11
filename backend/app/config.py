from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Neo4j Configuration
    neo4j_uri: str = "neo4j://127.0.0.1:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "hackathon2023"
    
    # API Configuration
    api_title: str = "Fund Referential API"
    api_version: str = "1.0.0"
    api_description: str = "API for managing fund hierarchies, relationships and compositions"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()