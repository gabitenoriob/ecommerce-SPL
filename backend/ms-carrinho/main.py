import consul
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import atexit
import socket
import models,schema, database
from fastapi.middleware.cors import CORSMiddleware

SERVICE_NAME = "ms-carrinho" 
SERVICE_ID = f"{SERVICE_NAME}-{socket.gethostname()}"
SERVICE_PORT = 8002 
SERVICE_HOST = "localhost" 

CONSUL_HOST = "localhost"
CONSUL_PORT = 8500
c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

traefik_tags = [
    f"traefik.enable=true",
    f"traefik.http.routers.{SERVICE_NAME}.rule=PathPrefix(`/api/carrinho`)", 
    f"traefik.http.routers.{SERVICE_NAME}.entrypoints=web",
    f"traefik.http.services.{SERVICE_NAME}.loadbalancer.server.port={SERVICE_PORT}"
]

def register_service():
    print(f"Registrando serviço {SERVICE_ID} no Consul...")
    c.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=SERVICE_HOST,
        port=SERVICE_PORT,
        tags=traefik_tags,
        check=consul.Check.http(
            f"http://{SERVICE_HOST}:{SERVICE_PORT}/api/carrinho/health", 
            "10s"
        )
    )

def deregister_service():
    print(f"Removendo serviço {SERVICE_ID} do Consul...")
    c.agent.service.deregister(service_id=SERVICE_ID)

app = FastAPI(title="Microserviço de Carrinho", root_path="/api/carrinho")
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

@app.on_event("startup")
async def startup_event():
    # Cria a tabela "itens_carrinho" no novo banco
    models.Base.metadata.create_all(bind=database.engine)
    register_service()

atexit.register(deregister_service)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 7. ENDPOINTS DA API (CRUD do Carrinho) ---

@app.get("/health")
async def health():
    return {"status": "ok"}

def get_carrinho_data(db: Session, user_id: str):
    itens = db.query(models.ItemCarrinho).filter(models.ItemCarrinho.user_id == user_id).all()
    valor_total = sum(item.preco_produto * item.quantidade for item in itens)
    return schema.Carrinho(user_id=user_id, items=itens, valor_total=valor_total)

@app.get("/{user_id}", response_model=schema.Carrinho)
async def obter_carrinho(user_id: str, db: Session = Depends(get_db)):
    return get_carrinho_data(db, user_id)

# Rota para ADICIONAR/ATUALIZAR um item
@app.post("/{user_id}", response_model=schema.Carrinho)
async def adicionar_item(
    user_id: str, 
    item: schema.ItemCreate, 
    db: Session = Depends(get_db)
):
    # 1. Verifica se o item JÁ EXISTE no carrinho deste usuário
    db_item = db.query(models.ItemCarrinho).filter(
        models.ItemCarrinho.user_id == user_id,
        models.ItemCarrinho.produto_id == item.produto_id
    ).first()

    if db_item:
        # Se existe, ATUALIZA a quantidade
        db_item.quantidade = item.quantidade
    else:
        # Se não existe, CRIA o novo item
        db_item = models.ItemCarrinho(
            user_id=user_id,
            produto_id=item.produto_id,
            nome_produto=item.nome_produto,
            preco_produto=item.preco_produto,
            quantidade=item.quantidade,
            imagem_url=item.imagem_url
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_item)

    # Retorna o carrinho completo atualizado
    return get_carrinho_data(db, user_id)

@app.delete("/{user_id}/{produto_id}", response_model=schema.Carrinho)
async def remover_item(user_id: str, produto_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.ItemCarrinho).filter(
        models.ItemCarrinho.user_id == user_id,
        models.ItemCarrinho.produto_id == produto_id
    ).first()

    if db_item:
        db.delete(db_item)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho")

    return get_carrinho_data(db, user_id)

@app.delete("/{user_id}/limpar")
async def limpar_carrinho(user_id: str, db: Session = Depends(get_db)):
    db.query(models.ItemCarrinho).filter(models.ItemCarrinho.user_id == user_id).delete()
    db.commit()
    return {"message": "Carrinho limpo com sucesso"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True
    )