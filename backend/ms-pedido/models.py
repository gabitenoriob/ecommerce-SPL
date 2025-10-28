from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# Usando o mesmo Enum do schema para consistência
from schema import StatusPedido

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    status = Column(SQLEnum(StatusPedido), default=StatusPedido.pendente, nullable=False)
    valor_total = Column(Float, nullable=False)
    # Adiciona data e hora de criação e atualização automáticas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com itens do pedido
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, nullable=False)
    nome_produto = Column(String, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    quantidade = Column(Integer, nullable=False)

    # Relacionamento com o pedido
    pedido = relationship("Pedido", back_populates="items")