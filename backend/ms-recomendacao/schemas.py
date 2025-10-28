from pydantic import BaseModel, Field
from typing import List, Optional

# --- Schemas de Resposta Interna (Simulando retorno do MS Pedido) ---

class ItemPedido(BaseModel):
    produto_id: str
    quantidade: int

class PedidoHistórico(BaseModel):
    id_pedido: str
    itens: List[ItemPedido]

# --- Schemas de Recomendação ---

class RecomendacaoProduto(BaseModel):
    produto_id: str
    nome: Optional[str] = Field(None, description="Nome do produto retornado pelo Catálogo.")
    motivo: str = Field(..., description="Motivo da recomendação (e.g., Comprado junto).")
    score: float = Field(..., description="Pontuação de relevância da recomendação.")

class RecomendacaoResponse(BaseModel):
    user_id: str
    recomendacoes: List[RecomendacaoProduto]
