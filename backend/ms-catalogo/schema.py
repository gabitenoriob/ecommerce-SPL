from pydantic import BaseModel

class ProdutoBase(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float
    imagem_url: str | None = None

# Schema para CRIAR um produto 
class ProdutoCreate(ProdutoBase):
    pass

# Schema para LER um produto (tem o ID e vem do DB)
class Produto(ProdutoBase):
    id: int

    class Config:
        from_attributes = True 
