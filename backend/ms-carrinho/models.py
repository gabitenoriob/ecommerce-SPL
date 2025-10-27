from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class ItemCarrinho(Base):
    __tablename__ = "itens_carrinho"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    produto_id = Column(Integer)
    nome_produto = Column(String)
    preco_produto = Column(Float)
    quantidade = Column(Integer)
    imagem_url = Column(String, nullable=True)