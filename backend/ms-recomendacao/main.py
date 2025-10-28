import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from typing import List
import httpx # Para fazer requisições HTTP para outros microserviços
import os

import schema # Arquivo schema.py que vamos criar

# --- Configurações do Serviço ---
SERVICE_HOST = "0.0.0.0"
# Usaremos a porta 8006 (seguindo a sequência)
SERVICE_PORT = 8006
# URL base para o microserviço de Pedidos (obtida via variável de ambiente ou configuração)
# No Docker Compose, podemos usar o nome do serviço: http://ms-pedido:8005
PEDIDO_SERVICE_URL = os.environ.get("PEDIDO_SERVICE_URL", "http://localhost:8005") # Fallback para dev local

app = FastAPI(
    title="Microserviço de Recomendações",
    description="Sugere produtos com base nos últimos pedidos do usuário.",
    # A rota no gateway será /api/recomendacoes, então o root_path reflete isso
    root_path="/api/recomendacoes"
)

# --- Lógica de Negócio (Simples) ---
async def buscar_ultimos_pedidos(user_id: str) -> List[dict]:
    """Busca os últimos pedidos do usuário no ms-pedido."""
    try:
        # Chama o endpoint do ms-pedido para listar pedidos do usuário
        # Ordena pelos mais recentes (assumindo que o ms-pedido suporte ordenação ou retorna em ordem)
        # Limita a um número razoável, ex: 5 últimos pedidos
        async with httpx.AsyncClient() as client:
            # NOTA: O endpoint /usuario/{user_id} no ms-pedido pode precisar
            # ser ajustado para suportar ordenação por data e limite.
            # Aqui, pegamos até 100 e filtramos depois (menos ideal).
            response = await client.get(f"{PEDIDO_SERVICE_URL}/usuario/{user_id}?limit=5") # Pega os últimos 5
            response.raise_for_status() # Lança exceção para erros HTTP (4xx, 5xx)
            pedidos = response.json()
            # Idealmente, o ms-pedido já retornaria ordenado decrescentemente por data.
            # Se não, precisaríamos ordenar aqui se a data estivesse disponível.
            return pedidos
    except httpx.HTTPStatusError as e:
        print(f"Erro ao buscar pedidos para {user_id}: {e.response.status_code} - {e.response.text}")
        # Retorna lista vazia ou lança uma exceção específica se preferir
        if e.response.status_code == 404:
            return [] # Usuário sem pedidos
        raise HTTPException(status_code=503, detail=f"Serviço de Pedidos indisponível ou falhou: {e.response.status_code}")
    except Exception as e:
        print(f"Erro inesperado ao buscar pedidos: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar histórico de pedidos.")

def extrair_produtos_recomendados(pedidos: List[dict]) -> List[schema.ProdutoRecomendado]:
    """Extrai produtos únicos dos últimos pedidos."""
    produtos_vistos = set()
    produtos_recomendados = []

    if not pedidos:
        return []

    # Itera sobre os pedidos (do mais recente para o mais antigo, se ordenado)
    for pedido in pedidos:
        if 'items' in pedido:
            for item in pedido['items']:
                produto_id = item.get('produto_id')
                if produto_id and produto_id not in produtos_vistos:
                    produtos_recomendados.append(schema.ProdutoRecomendado(
                        produto_id=produto_id,
                        nome_produto=item.get('nome_produto', 'Nome não disponível'),
                        # Adicionar mais detalhes se o ms-pedido retornar (ex: imagem_url)
                    ))
                    produtos_vistos.add(produto_id)
                    # Limita a um número máximo de recomendações, ex: 5
                    if len(produtos_recomendados) >= 5:
                        break
            if len(produtos_recomendados) >= 5:
                break

    return produtos_recomendados

# --- Endpoints ---
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ms-recomendacao"}

@app.get("/{user_id}", response_model=schema.RecomendacaoResponse)
async def get_recomendacoes(user_id: str):
    """Retorna recomendações de produtos para um usuário com base nos últimos pedidos."""
    ultimos_pedidos = await buscar_ultimos_pedidos(user_id)

    if not ultimos_pedidos:
        # Se não há pedidos, podemos retornar vazio ou sugestões genéricas
        # Por enquanto, retornamos vazio.
         return schema.RecomendacaoResponse(user_id=user_id, produtos_recomendados=[])
        # raise HTTPException(status_code=404, detail="Nenhum pedido encontrado para gerar recomendações.")

    produtos = extrair_produtos_recomendados(ultimos_pedidos)

    if not produtos:
         return schema.RecomendacaoResponse(user_id=user_id, produtos_recomendados=[])
        # raise HTTPException(status_code=404, detail="Não foi possível extrair produtos para recomendação.")


    return schema.RecomendacaoResponse(
        user_id=user_id,
        produtos_recomendados=produtos
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=True # Modo de desenvolvimento
    )