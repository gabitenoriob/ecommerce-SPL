from fastapi import FastAPI, HTTPException
from typing import Dict, List
import httpx
import os
from schema import (
    DetalhesPedido, PedidoCriadoResponse, StatusPedido, 
    CarrinhoDetalhes, PagamentoAprovado, ItemCarrinhoDetalhado, 
    StatusPagamento
)
#finalizar e comprar
# --- Configurações de Comunicação ---
# No ambiente Docker Compose, usamos o nome do serviço (ex: ms-carrinho) para o host.
CARRINHO_SERVICE_URL = os.getenv("CARRINHO_SERVICE_URL", "http://ms-carrinho:8002/api/carrinho")
PAGAMENTO_SERVICE_URL = os.getenv("PAGAMENTO_SERVICE_URL", "http://ms-pagamento:8004/api/pagamento")

# --- Simulação de Banco de Dados de Pedidos ---
# Armazenamento em memória (em um projeto real, usaria um banco de dados)
db_pedidos: Dict[str, PedidoCriadoResponse] = {}
next_order_id = 1

app = FastAPI(
    title="Microserviço de Pedidos",
    description="Orquestra o checkout, pagamento e finalização da compra.",
    openapi_url="/api/pedido/openapi.json",
    docs_url="/api/pedido/docs",
    redoc_url="/api/pedido/redoc"
)

async def fetch_carrinho_details(user_id: str) -> CarrinhoDetalhes:
    """Busca detalhes do carrinho do usuário."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CARRINHO_SERVICE_URL}/{user_id}")
            response.raise_for_status()
            
            carrinho_data = response.json()
            # Certifica-se de que o carrinho não está vazio
            if not carrinho_data.get('itens'):
                 raise HTTPException(status_code=400, detail="Carrinho vazio. Não é possível finalizar a compra.")
                
            return CarrinhoDetalhes(**carrinho_data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                 raise HTTPException(status_code=404, detail="Carrinho não encontrado para este usuário.")
            raise HTTPException(status_code=503, detail=f"Erro ao comunicar com MS Carrinho: {e.response.text}")
        except Exception as e:
            # Em produção, logging seria mais detalhado
            raise HTTPException(status_code=500, detail=f"Erro inesperado ao buscar carrinho: {e}")

async def process_pagamento(user_id: str, valor_total: float, metodo: str) -> PagamentoAprovado:
    """Chama o MS de Pagamento para processar a transação."""
    payload = {
        "user_id": user_id,
        "valor_total": valor_total,
        "metodo_pagamento": metodo
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{PAGAMENTO_SERVICE_URL}/", json=payload)
            response.raise_for_status()
            
            pagamento_data = response.json()
            return PagamentoAprovado(
                id_pagamento=pagamento_data["id_pagamento"],
                status=pagamento_data["status"]
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=503, detail=f"Erro ao processar pagamento: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado ao chamar pagamento: {e}")

async def clear_carrinho(user_id: str):
    """Limpa o carrinho após a compra ser finalizada/aprovada."""
    async with httpx.AsyncClient() as client:
        try:
            # Assumindo que o MS Carrinho tem um endpoint para exclusão
            await client.delete(f"{CARRINHO_SERVICE_URL}/limpar/{user_id}")
        except Exception as e:
            # Logar o erro, mas não impedir o retorno do pedido (pois o pagamento foi feito)
            print(f"ATENÇÃO: Não foi possível limpar o carrinho do usuário {user_id}. Erro: {e}")


# Endpoint principal para finalizar a compra
@app.post("/checkout/", response_model=PedidoCriadoResponse)
async def finalizar_compra(detalhes: DetalhesPedido):
    global next_order_id
    
    user_id = detalhes.user_id
    order_id = f"ORD-{next_order_id:04}"
    
    # 1. Busca e valida os detalhes do carrinho
    carrinho_detalhes = await fetch_carrinho_details(user_id)
    valor_total = carrinho_detalhes.valor_total

    # 2. Processa o pagamento
    pagamento_status = await process_pagamento(
        user_id=user_id, 
        valor_total=valor_total, 
        metodo=detalhes.metodo_pagamento
    )

    # 3. Lógica Pós-Pagamento
    
    # Prepara a resposta inicial do Pedido
    base_response = PedidoCriadoResponse(
        id_pedido=order_id,
        user_id=user_id,
        valor_total=valor_total,
        itens=carrinho_detalhes.itens,
        status=StatusPedido.rejeitado, # Default para ser sobrescrito
        mensagem="Houve um erro no processamento do pedido."
    )
    
    if pagamento_status.status == StatusPagamento.aprovado:
        # APROVADO: Muda status e limpa carrinho
        base_response.status = StatusPedido.aprovado
        base_response.mensagem = f"Compra finalizada com sucesso! ID do Pagamento: {pagamento_status.id_pagamento}. Seu pedido está sendo processado."
        
        # Limpa o carrinho (operação assíncrona, mas pode ser "fire-and-forget")
        await clear_carrinho(user_id)
        
    elif pagamento_status.status == StatusPagamento.rejeitado:
        # REJEITADO: Mantém o carrinho intacto
        base_response.status = StatusPedido.rejeitado
        base_response.mensagem = "Pagamento foi rejeitado. Tente novamente ou use outro método de pagamento."
        
    else:
        # OUTROS STATUS (Pendente, Cancelado)
        base_response.status = StatusPedido.processando
        base_response.mensagem = f"Pagamento em status {pagamento_status.status}. Seu pedido está em análise."
    
    # 4. Salva o pedido final e incrementa ID
    db_pedidos[order_id] = base_response
    next_order_id += 1
    
    return base_response

# Endpoint de saúde/cheque
@app.get("/health/")
def health_check():
    return {"status": "ok", "service": "ms-pedido"}
