from fastapi import FastAPI, HTTPException
from typing import Dict, List, Set, Tuple
import httpx
import os
from schema import RecomendacaoResponse, RecomendacaoProduto, PedidoHistórico, ItemPedido

# --- Configurações de Comunicação ---
# URL para o MS de Pedidos (para buscar o histórico)
PEDIDO_SERVICE_URL = os.getenv("PEDIDO_SERVICE_URL", "http://ms-pedido:8005/api/pedido")
# URL para o MS de Catálogo (para buscar detalhes dos produtos recomendados)
CATALOGO_SERVICE_URL = os.getenv("CATALOGO_SERVICE_URL", "http://ms-catalogo:8001/api/catalogo")

app = FastAPI(
    title="Microserviço de Recomendação",
    description="Gera recomendações de produtos baseadas no histórico de compras.",
    openapi_url="/api/recomendacao/openapi.json",
    docs_url="/api/recomendacao/docs",
    redoc_url="/api/recomendacao/redoc"
)

# Base de afinidade de produtos (simulação de um modelo de ML)
# Se o usuário compra X, recomende Y
PRODUTOS_AFINIDADE: Dict[str, List[Tuple[str, str]]] = {
    # Se comprou Fone de Ouvido (PROD-001), recomende Capa de Celular (PROD-004)
    "PROD-001": [("PROD-004", "Combina com seu smartphone."), ("PROD-003", "Acessórios complementares.")],
    # Se comprou Câmera (PROD-002), recomende Cartão de Memória (PROD-005)
    "PROD-002": [("PROD-005", "Não se esqueça do cartão de memória!"), ("PROD-001", "Outros gadgets.")],
    # Se comprou Cartão de Memória (PROD-005), recomende Câmera (PROD-002)
    "PROD-005": [("PROD-002", "O produto principal para este acessório.")],
}

async def fetch_historico_pedidos(user_id: str) -> List[PedidoHistórico]:
    """Busca o histórico de pedidos do usuário (simulação: chamando MS Pedido)."""
    # NO SISTEMA REAL, O MS PEDIDO TERIA UM ENDPOINT COMO: /historico/{user_id}
    # Como não modificamos o MS Pedido para ter um endpoint de histórico, 
    # vamos simular o retorno de dados aqui para manter a funcionalidade do MS Recomendacao.

    # Simulação de dados de histórico para fins de teste
    if user_id == "user_gabriel":
        return [
            PedidoHistórico(id_pedido="ORD-0001", itens=[ItemPedido(produto_id="PROD-001", quantidade=1)]),
            PedidoHistórico(id_pedido="ORD-0002", itens=[ItemPedido(produto_id="PROD-002", quantidade=1), ItemPedido(produto_id="PROD-003", quantidade=2)]),
        ]
    elif user_id == "user_ana":
        return [
            PedidoHistórico(id_pedido="ORD-0003", itens=[ItemPedido(produto_id="PROD-005", quantidade=10)]),
        ]
    return []

async def fetch_nome_produto(produto_id: str) -> str:
    """Busca o nome do produto no MS Catálogo."""
    async with httpx.AsyncClient() as client:
        try:
            # Assumindo que o MS Catálogo tem um endpoint para buscar detalhes de um produto
            response = await client.get(f"{CATALOGO_SERVICE_URL}/produtos/{produto_id}")
            response.raise_for_status()
            
            # Catálogo retorna um objeto Produto com campo 'nome'
            return response.json().get("nome", f"Produto {produto_id}") 
        except Exception:
            # Falha silenciosa se o Catálogo estiver fora ou o produto não existir
            return f"Produto {produto_id}"

@app.get("/sugerir/{user_id}", response_model=RecomendacaoResponse)
async def sugerir_produtos(user_id: str):
    # 1. Busca Histórico de Compras
    historico = await fetch_historico_pedidos(user_id)
    
    if not historico:
        # Se não há histórico, retorna recomendações default (ex: mais vendidos)
        default_recs = [
            RecomendacaoProduto(produto_id="PROD-001", nome="Fone Default", motivo="Mais vendidos.", score=0.8),
            RecomendacaoProduto(produto_id="PROD-002", nome="Câmera Default", motivo="Mais vendidos.", score=0.7),
        ]
        return RecomendacaoResponse(user_id=user_id, recomendacoes=default_recs)

    # 2. Extrai Itens Comprados (evitando duplicação no set)
    comprados_ids: Set[str] = set()
    for pedido in historico:
        for item in pedido.itens:
            comprados_ids.add(item.produto_id)

    # 3. Gera Recomendações Baseadas em Afinidade
    recomendacoes_map: Dict[str, RecomendacaoProduto] = {}
    
    for produto_id in comprados_ids:
        if produto_id in PRODUTOS_AFINIDADE:
            for rec_id, motivo in PRODUTOS_AFINIDADE[produto_id]:
                # Evita recomendar o que o usuário já comprou
                if rec_id not in comprados_ids and rec_id not in recomendacoes_map:
                    # Score simples baseado na ordem de afinidade (1.0 - 0.1 * index)
                    score = 1.0 - (list(PRODUTOS_AFINIDADE[produto_id]).index((rec_id, motivo)) * 0.1)
                    
                    recomendacoes_map[rec_id] = RecomendacaoProduto(
                        produto_id=rec_id,
                        motivo=motivo,
                        score=round(score, 2)
                    )

    # 4. Busca Nomes dos Produtos (Chamada paralela para o Catálogo)
    recomendacoes_finais = list(recomendacoes_map.values())
    
    # Criando uma lista de tarefas assíncronas para buscar nomes
    tasks = [fetch_nome_produto(rec.produto_id) for rec in recomendacoes_finais]
    
    # Simulação da execução concorrente (usaria asyncio.gather em código real)
    # Aqui, fazemos uma iteração simples por simplicidade de ambiente
    for rec in recomendacoes_finais:
        rec.nome = await fetch_nome_produto(rec.produto_id)

    # 5. Ordena por Score e Retorna
    recomendacoes_finais.sort(key=lambda r: r.score, reverse=True)

    return RecomendacaoResponse(user_id=user_id, recomendacoes=recomendacoes_finais)

# Endpoint de saúde/cheque
@app.get("/health/")
def health_check():
    return {"status": "ok", "service": "ms-recomendacao"}
