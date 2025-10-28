from pydantic import BaseModel
from typing import List, Optional

# Schema para um produto recomendado (simplificado)
class ProdutoRecomendado(BaseModel):
    produto_id: int
    nome_produto: str
    # Poderia adicionar imagem_url, preço, etc., se buscássemos no ms-catalogo
    # imagem_url: Optional[str] = None

# Schema para a resposta da API de recomendação
class RecomendacaoResponse(BaseModel):
    user_id: str
    produtos_recomendados: List[ProdutoRecomendado]