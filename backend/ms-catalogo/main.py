import consul
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import socket
import models
import schema
import database
from typing import List 

from fastapi.middleware.cors import CORSMiddleware
# --- Configurações do Serviço ---
SERVICE_NAME = "ms-catalogo"
SERVICE_ID = f"{SERVICE_NAME}-{socket.gethostname()}"
SERVICE_PORT = 8001
SERVICE_HOST = "localhost" 

# --- Configurações do Consul ---
CONSUL_HOST = "localhost"
CONSUL_PORT = 8500
c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

# Tags do Traefik (Gateway)
traefik_tags = [
    f"traefik.enable=true",
    f"traefik.http.routers.{SERVICE_NAME}.rule=PathPrefix(`/api/catalogo`)",
    f"traefik.http.routers.{SERVICE_NAME}.entrypoints=web",
    f"traefik.http.services.{SERVICE_NAME}.loadbalancer.server.port={SERVICE_PORT}"
]

# --- Funções de Registro no Consul ---
def register_service():
    print(f"Registrando serviço {SERVICE_ID} no Consul...")
    c.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=SERVICE_HOST,
        port=SERVICE_PORT,
        tags=traefik_tags,
        check=consul.Check.http(
            # O health check precisa incluir o root_path
            f"http://{SERVICE_HOST}:{SERVICE_PORT}/api/catalogo/health", 
            "10s"
        )
    )

def deregister_service():
    print(f"Removendo serviço {SERVICE_ID} do Consul...")
    c.agent.service.deregister(service_id=SERVICE_ID)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run ON STARTUP ---
    register_service()
    print("Application is starting up...")
    
    yield # O aplicativo fica em execução aqui
    
    # --- Code to run ON SHUTDOWN ---
    deregister_service()
    print("Application is shutting down...")

app = FastAPI(
    title="Microserviço de Catálogo", 
    root_path="/api/catalogo", 
    lifespan=lifespan
)
origins = [
    "http://localhost:5173",
    "http://localhost:3000", 
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Quais URLs podem fazer requisições
    allow_credentials=True,    # Permite cookies (se houver)
    allow_methods=["*"],       # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],       # Permite todos os cabeçalhos
)
# A linha 'atexit.register(deregister_service)' foi removida

# Esta função gerencia a sessão do banco de dados para cada requisição
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints da API (CRUD) ---

# Health check para o Consul (acessível em /api/catalogo/health)
@app.get("/health")
async def health():
    return {"status": "ok"}

# Rota para CRIAR um produto (POST)
@app.post("/produtos/", response_model=schema.Produto)
async def create_produto(
    produto: schema.ProdutoCreate, 
    db: Session = Depends(get_db)
):
    db_produto = models.Produto(
        nome=produto.nome,
        descricao=produto.descricao,
        preco=produto.preco,
        imagem_url=produto.imagem_url
    )
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

# Rota para LER produtos (GET)
@app.get("/produtos/", response_model=List[schema.Produto])
async def read_produtos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    produtos = db.query(models.Produto).offset(skip).limit(limit).all()
    return produtos

# Rota para LER um produto específico (GET por ID)
@app.get("/produtos/{produto_id}", response_model=schema.Produto)
async def read_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if db_produto is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return db_produto

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True 
    )