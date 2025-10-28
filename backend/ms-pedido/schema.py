from pydantic import BaseModel, Field
from typing import List
from enum import Enum

# --- Schemas de Resposta Interna (simulando retorno de outros MS) ---

# Reutilizando o status do MS de Pagamento
class StatusPagamento(str, Enum):
    pendente = "Pendente"
    aprovado = "Aprovado"
    rejeitado = "Rejeitado"
    cancelado = "Cancelado"

class ItemCarrinhoDetalhado(BaseModel):
    produto_id: str
    nome: str
    preco: float
    quantidade: int

class CarrinhoDetalhes(BaseModel):
    user_id: str
    itens: List[ItemCarrinhoDetalhado]
    valor_total: float

class PagamentoAprovado(BaseModel):
    id_pagamento: str
    status: StatusPagamento

# --- Schemas de Pedido (Ordem de Compra) ---

class StatusPedido(str, Enum):
    pendente = "Pendente"
    processando = "Processando"
    aprovado = "Aprovado"
    rejeitado = "Rejeitado"
    enviado = "Enviado"

class DetalhesPedido(BaseModel):
    user_id: str = Field(..., description="ID do usuário que está finalizando a compra.")
    metodo_pagamento: str = Field(..., description="Método de pagamento escolhido.")
    frete_id: str = Field(..., description="ID/código do frete escolhido.")

class PedidoCriadoResponse(BaseModel):
    id_pedido: str
    user_id: str
    valor_total: float
    status: StatusPedido
    itens: List[ItemCarrinhoDetalhado]
    mensagem: str
