import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schema, database, crud # Vamos criar um crud.py para organizar

# --- Configurações do Serviço ---
SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 8005 # <-- Nova porta para este serviço

app = FastAPI(title="Microserviço de Pedidos", root_path="/api/pedidos")

# Cria as tabelas no banco de dados quando a aplicação inicia
@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=database.engine)

# Dependência para obter a sessão do banco de dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/", response_model=schema.Pedido, status_code=status.HTTP_201_CREATED)
def create_pedido(pedido: schema.PedidoCreate, db: Session = Depends(get_db)):
    """Cria um novo pedido."""
    # Validação simples do valor total (poderia ser mais complexa)
    valor_calculado = sum(item.preco_unitario * item.quantidade for item in pedido.items)
    # Aqui você pode adicionar lógica para verificar se o valor bate com o carrinho, etc.
    
    # Cria o pedido no banco usando a função do crud.py (a ser criada)
    return crud.create_pedido(db=db, pedido=pedido, valor_total=valor_calculado)

@app.get("/{pedido_id}", response_model=schema.Pedido)
def read_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Obtém os detalhes de um pedido específico."""
    db_pedido = crud.get_pedido(db, pedido_id=pedido_id)
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_pedido

@app.get("/usuario/{user_id}", response_model=List[schema.Pedido])
def read_pedidos_usuario(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista os pedidos de um usuário específico."""
    pedidos = crud.get_pedidos_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return pedidos

@app.patch("/{pedido_id}/status", response_model=schema.Pedido)
def update_status_pedido(pedido_id: int, status_update: schema.PedidoUpdateStatus, db: Session = Depends(get_db)):
    """Atualiza o status de um pedido."""
    db_pedido = crud.update_pedido_status(db, pedido_id=pedido_id, status=status_update.status)
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_pedido


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=True
    )