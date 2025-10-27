from pydantic import BaseModel

# Schema para criar/atualizar um item
class ItemCreate(BaseModel):
    produto_id: int
    nome_produto: str
    preco_produto: float
    quantidade: int
    imagem_url: Optional[str] = None

# Schema para ler um item (vem do DB, tem id)
class Item(ItemCreate):
    id: int
    user_id: str

    class Config:
        from_attributes = True

# Schema para o carrinho completo
class Carrinho(BaseModel):
    user_id: str
    items: list[Item]
    valor_total: float