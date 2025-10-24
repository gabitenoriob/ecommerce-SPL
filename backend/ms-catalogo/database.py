from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# Cria a "engine" de conexão com o DB
engine = create_engine(settings.database_url)

# Cria uma fábrica de "sessões" (conexões)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nossos modelos (tabelas)
Base = declarative_base()
