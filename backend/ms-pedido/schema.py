from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import enum

# Enum para representar os possíveis status de um pedido
class StatusPedido(str, enum.Enum):
    pendente = "Pendente"
    processando = "Processando"
    enviado = "Enviado"
    entregue = "Entregue"
    cancelado = "Cancelado"

# Schema base para um item de pedido (usado na criação)
class ItemPedidoBase(BaseModel):
    produto_id: int
    nome_produto: str
    preco_unitario: float
    quantidade: int = Field(..., gt=0) # Quantidade deve ser maior que 0

# Schema para ler um item de pedido (inclui id)
class ItemPedido(ItemPedidoBase):
    id: int
    pedido_id: int

    class Config:
        from_attributes = True # Permite mapear do modelo SQLAlchemy

# Schema base para um pedido (usado na criação)
class PedidoBase(BaseModel):
    user_id: str
    items: List[ItemPedidoBase] # Para criar, recebemos apenas os dados base dos itens

# Schema para criar um pedido (não precisa de status ou valor total inicialmente)
class PedidoCreate(PedidoBase):
    pass

# Schema para ler um pedido (resposta da API)
class Pedido(PedidoBase):
    id: int
    status: StatusPedido
    valor_total: float
    created_at: Optional[datetime] = None # Tornando opcional para leitura inicial
    updated_at: Optional[datetime] = None # Tornando opcional para leitura inicial
    items: List[ItemPedido] # Para ler, retornamos os itens completos com ID

    class Config:
        from_attributes = True # Permite mapear do modelo SQLAlchemy

# Schema para atualização de status (exemplo)
class PedidoUpdateStatus(BaseModel):
    status: StatusPedido