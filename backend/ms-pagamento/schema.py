from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# Enum para representar os possíveis estados do pagamento
class StatusPagamento(str, Enum):
    pendente = "Pendente"
    aprovado = "Aprovado"
    rejeitado = "Rejeitado"
    cancelado = "Cancelado"

# Request: Dados que o cliente envia para iniciar um pagamento
class PagamentoRequest(BaseModel):
    user_id: str = Field(..., description="ID do usuário que está pagando.")
    carrinho_id: Optional[str] = Field(None, description="ID do carrinho (opcional, pode ser o mesmo do user_id).")
    valor_total: float = Field(..., gt=0, description="Valor total a ser pago.")
    metodo_pagamento: str = Field(..., description="Ex: 'cartao_credito', 'boleto', 'pix'.")

# Response: Retorno do estado de um pagamento
class PagamentoResponse(BaseModel):
    id_pagamento: str
    user_id: str
    valor: float
    status: StatusPagamento
    mensagem: str = Field(..., description="Mensagem de status para o cliente.")

# Request: Dados para consultar o status de um pagamento
class ConsultaStatus(BaseModel):
    id_pagamento: str