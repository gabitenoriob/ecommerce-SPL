import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schema, database
from typing import List

# --- REMOVEMOS TODO O CÓDIGO DO CONSUL ---

# --- Configurações do Serviço ---
# O Host 0.0.0.0 é CRÍTICO para rodar no Docker
# A Porta 8001 DEVE BATER com o label do docker-compose
SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 8001 

app = FastAPI(title="Microserviço de Catálogo", root_path="/api/catalogo")

# --- O CORS FOI REMOVIDO DAQUI ---
# (O Traefik deve cuidar disso, como expliquei antes)

@app.on_event("startup")
async def startup_event():
    # Só precisamos criar as tabelas
    models.Base.metadata.create_all(bind=database.engine)

# --- O atexit FOI REMOVIDO ---

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints (O CRUD continua igual) ---

@app.get("/health")
async def health():
    return {"status": "ok"}

# (Cole aqui suas rotas: create_produto, read_produtos, read_produto)
# ...
@app.get("/produtos/", response_model=List[schema.Produto])
async def read_produtos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    produtos = db.query(models.Produto).offset(skip).limit(limit).all()
    return produtos

# ... (outras rotas do CRUD)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True # O reload=True não é ideal em produção, mas ok para dev
    )
