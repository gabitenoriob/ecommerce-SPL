import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schema, database

# --- REMOVEMOS TODO O CÓDIGO DO CONSUL ---

# --- Configurações do Serviço ---
SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 8002 # <-- Porta 8002

app = FastAPI(title="Microserviço de Carrinho", root_path="/api/carrinho")

@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints (O CRUD do carrinho continua igual) ---
@app.get("/health")
async def health():
    return {"status": "ok"}

# (Cole aqui suas rotas: get_carrinho_data, obter_carrinho, adicionar_item, etc.)
# ...
@app.get("/{user_id}", response_model=schema.Carrinho)
async def obter_carrinho(user_id: str, db: Session = Depends(get_db)):
    itens = db.query(models.ItemCarrinho).filter(models.ItemCarrinho.user_id == user_id).all()
    valor_total = sum(item.preco_produto * item.quantidade for item in itens)
    return schema.Carrinho(user_id=user_id, items=itens, valor_total=valor_total)

# ... (outras rotas do CRUD)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True
    )
