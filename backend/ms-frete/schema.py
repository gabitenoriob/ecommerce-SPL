from pydantic import BaseModel
from typing import List
# O que a API espera receber no body do POST
class FreteRequest(BaseModel):
    cep: str
   

# Uma única opção de frete
class OpcaoFrete(BaseModel):
    metodo: str  # Ex: "SEDEX", "PAC"
    prazo_dias: int
    valor: float

# A resposta completa da API
class FreteResponse(BaseModel):
    opcoes: List[OpcaoFrete]