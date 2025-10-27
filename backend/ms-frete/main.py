import consul
import uvicorn
from fastapi import FastAPI, HTTPException
import atexit
import socket

# Importa nossos novos schemas
from . import schemas

# --- 1. CONFIGURAÇÕES DO SERVIÇO (Modificadas) ---
SERVICE_NAME = "ms-frete" 
SERVICE_ID = f"{SERVICE_NAME}-{socket.gethostname()}"
SERVICE_PORT = 8003 
SERVICE_HOST = "localhost" 

# --- 2. CONFIGURAÇÕES DO CONSUL (Iguais) ---
CONSUL_HOST = "localhost"
CONSUL_PORT = 8500
c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

# --- 3. CONFIGURAÇÕES DO TRAEFIK (Modificadas) ---
traefik_tags = [
    f"traefik.enable=true",
    f"traefik.http.routers.{SERVICE_NAME}.rule=PathPrefix(`/api/frete`)", 
    f"traefik.http.routers.{SERVICE_NAME}.entrypoints=web",
    f"traefik.http.services.{SERVICE_NAME}.loadbalancer.server.port={SERVICE_PORT}"
]

# --- 4. FUNÇÕES DE REGISTRO (Modificadas) ---
def register_service():
    print(f"Registrando serviço {SERVICE_ID} no Consul...")
    c.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address=SERVICE_HOST,
        port=SERVICE_PORT,
        tags=traefik_tags,
        check=consul.Check.http(
            f"http://{SERVICE_HOST}:{SERVICE_PORT}/api/frete/health", 
            "10s"
        )
    )

def deregister_service():
    print(f"Removendo serviço {SERVICE_ID} do Consul...")
    c.agent.service.deregister(service_id=SERVICE_ID)

# --- 5. INICIALIZAÇÃO DO APP (Modificado) ---
app = FastAPI(title="Microserviço de Frete", root_path="/api/frete") # <-- MUDOU

@app.on_event("startup")
async def startup_event():
    # Não precisa criar tabela, só registrar
    register_service()

atexit.register(deregister_service)

# --- 6. ENDPOINTS DA API (Lógica de Frete) ---

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Rota principal para CALCULAR o frete
@app.post("/calcular", response_model=schemas.FreteResponse)
async def calcular_frete(request: schemas.FreteRequest):
    """
    Simula o cálculo de frete.
    A lógica é 100% "mockada" (falsa) apenas para fins de demonstração.
    """
    opcoes = []

    # Remove traços e formata o CEP
    cep = request.cep.replace("-", "").strip()

    if not cep.isdigit() or len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido. Deve conter 8 números.")

    # Lógica de simulação:
    if cep.startswith("57"): # CEPs de Alagoas (ex: 57000-000)
        opcoes.append(schemas.OpcaoFrete(metodo="SEDEX Local", prazo_dias=1, valor=15.00))
        opcoes.append(schemas.OpcaoFrete(metodo="Entrega por Motoboy", prazo_dias=0, valor=25.00))

    elif cep.startswith("01"): # CEPs de São Paulo (ex: 01000-000)
        opcoes.append(schemas.OpcaoFrete(metodo="PAC", prazo_dias=7, valor=30.50))
        opcoes.append(schemas.OpcaoFrete(metodo="SEDEX", prazo_dias=3, valor=55.00))

    else: # Qualquer outro CEP
        opcoes.append(schemas.OpcaoFrete(metodo="PAC Padrão", prazo_dias=10, valor=28.00))

    if not opcoes:
         raise HTTPException(status_code=404, detail="Não há opções de entrega para este CEP.")

    return schemas.FreteResponse(opcoes=opcoes)

# --- 8. PONTO DE ENTRADA (Igual) ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True
    )