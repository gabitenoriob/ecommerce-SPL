from pydantic import BaseModel
from typing import Optional

class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    imagem_url: Optional[str] = None

# Schema para CRIAR um produto 
class ProdutoCreate(ProdutoBase):
    pass

# Schema para LER um produto (tem o ID e vem do DB)
class Produto(ProdutoBase):
    id: int

    class Config:
        from_attributes = True 
