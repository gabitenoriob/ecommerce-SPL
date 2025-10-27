from fastapi import FastAPI, HTTPException
from typing import Dict
from schema import PagamentoRequest, PagamentoResponse, StatusPagamento

# Dicionário simples para simular o banco de dados de pagamentos
# Chave: id_pagamento, Valor: objeto PagamentoResponse
db_pagamentos: Dict[str, PagamentoResponse] = {}
next_id = 1

app = FastAPI(
    title="Microserviço de Pagamento",
    description="Responsável por processar pagamentos.",
    # Configuração do Traefik/Consul para Descoberta de Serviço
    openapi_url="/api/pagamento/openapi.json",
    docs_url="/api/pagamento/docs",
    redoc_url="/api/pagamento/redoc"
)

# Simulando um processador de pagamento
def processar_pagamento_simulado(request: PagamentoRequest) -> StatusPagamento:
    """Simula a lógica de aprovação/rejeição."""
    # Simulação: rejeita pagamentos com valor ímpar
    if int(request.valor_total) % 2 != 0:
        return StatusPagamento.rejeitado
    # Simulação: aprova o restante
    return StatusPagamento.aprovado

# Endpoint 1: Iniciar um novo pagamento
@app.post("/pagamento/", response_model=PagamentoResponse)
def iniciar_pagamento(request: PagamentoRequest):
    global next_id

    # 1. Simula o processamento do pagamento
    status = processar_pagamento_simulado(request)
    id_pagamento = f"PAY-{next_id:04}"
    next_id += 1

    # 2. Cria o objeto de resposta
    if status == StatusPagamento.aprovado:
        mensagem = "Pagamento aprovado com sucesso."
    else:
        mensagem = "Pagamento rejeitado pela operadora."

    pagamento = PagamentoResponse(
        id_pagamento=id_pagamento,
        user_id=request.user_id,
        valor=request.valor_total,
        status=status,
        mensagem=mensagem
    )

    # 3. Salva no "banco de dados" simulado
    db_pagamentos[id_pagamento] = pagamento
    
    return pagamento

# Endpoint 2: Consultar status de um pagamento
@app.get("/pagamento/{id_pagamento}", response_model=PagamentoResponse)
def consultar_status(id_pagamento: str):
    if id_pagamento not in db_pagamentos:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    return db_pagamentos[id_pagamento]

# Endpoint de saúde/cheque
@app.get("/health/")
def health_check():
    return {"status": "ok", "service": "ms-pagamento"}

