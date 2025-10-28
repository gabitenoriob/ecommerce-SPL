import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schema, database

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

# --- Endpoints ---

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/{user_id}", response_model=schema.Carrinho)
async def obter_carrinho(user_id: str, db: Session = Depends(get_db)):
    """
    Obtém o carrinho completo de um usuário.
    """
    itens = db.query(models.ItemCarrinho).filter(models.ItemCarrinho.user_id == user_id).all()
    valor_total = sum(item.preco_produto * item.quantidade for item in itens)
    return schema.Carrinho(user_id=user_id, items=itens, valor_total=valor_total)

# --- ROTA ADICIONADA (Obrigatória para 'handleAddToCart') ---
@app.post("/{user_id}", response_model=schema.Carrinho)
async def adicionar_item(
    user_id: str, 
    item: schema.ItemCreate, # <-- Recebe o payload do frontend
    db: Session = Depends(get_db)
):
    """
    Adiciona um item ao carrinho ou atualiza sua quantidade.
    O frontend (App.tsx) já calcula a nova quantidade total.
    """
    # 1. Verifica se o item (mesmo produto) já existe no carrinho deste usuário
    db_item = db.query(models.ItemCarrinho).filter(
        models.ItemCarrinho.user_id == user_id,
        models.ItemCarrinho.produto_id == item.produto_id
    ).first()

    if db_item:
        # 2. Se existir, atualiza a quantidade
        db_item.quantidade = item.quantidade 
    else:
        # 3. Se não existir, cria um novo item no banco
        db_item = models.ItemCarrinho(
            user_id=user_id,
            produto_id=item.produto_id,
            nome_produto=item.nome_produto,
            preco_produto=item.preco_produto,
            quantidade=item.quantidade,
            imagem_url=item.imagem_url
        )
        db.add(db_item)

    # 4. Salva as mudanças no banco
    db.commit()

    # 5. Retorna o carrinho completo e atualizado
    itens = db.query(models.ItemCarrinho).filter(models.ItemCarrinho.user_id == user_id).all()
    valor_total = sum(i.preco_produto * i.quantidade for i in itens)
    
    return schema.Carrinho(user_id=user_id, items=itens, valor_total=valor_total)

# --- ROTA ADICIONADA (Obrigatória para 'handleRemoveFromCart') ---
@app.delete("/{user_id}/{produto_id}", response_model=schema.Carrinho)
async def remover_item(
    user_id: str, 
    produto_id: int, 
    db: Session = Depends(get_db)
):
    """
    Remove um item específico do carrinho do usuário.
    """
    # 1. Encontra o item
    db_item = db.query(models.ItemCarrinho).filter(
        models.ItemCarrinho.user_id == user_id,
        models.ItemCarrinho.produto_id == produto_id
    ).first()

    if db_item:
        # 2. Deleta o item se ele existir
        db.delete(db_item)
        db.commit()
    
    # 3. Retorna o carrinho atualizado (mesmo que o item não exista)
    itens = db.query(models.ItemCarrinho).filter(models.ItemCarrinho.user_id == user_id).all()
    valor_total = sum(i.preco_produto * i.quantidade for i in itens)
    return schema.Carrinho(user_id=user_id, items=itens, valor_total=valor_total)

# --- ROTA ADICIONADA (Obrigatória para 'handleFinalizarCompra') ---
@app.delete("/{user_id}/limpar", response_model=schema.Carrinho)
async def limpar_carrinho(user_id: str, db: Session = Depends(get_db)):
    """
    Remove TODOS os itens do carrinho de um usuário,
    geralmente após uma compra ser finalizada.
    """
    # 1. Deleta todos os itens para este usuário
    db.query(models.ItemCarrinho).filter(
        models.ItemCarrinho.user_id == user_id
    ).delete()
    
    db.commit()

    # 2. Retorna um carrinho vazio
    return schema.Carrinho(user_id=user_id, items=[], valor_total=0.0)

# --- Ponto de entrada ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True
    )