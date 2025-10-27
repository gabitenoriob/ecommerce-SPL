import uvicorn
from fastapi import FastAPI, HTTPException
import schema

# --- REMOVEMOS TODO O CÓDIGO DO CONSUL ---

# --- Configurações do Serviço ---
SERVICE_HOST = "0.0.0.0"
SERVICE_PORT = 8003 # <-- Porta 8003 (como definimos no compose)

app = FastAPI(title="Microserviço de Frete", root_path="/api/frete")

# --- Não precisamos de @app.on_event("startup") ---

# --- Endpoints (A lógica do mock continua igual) ---
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/calcular", response_model=schema.FreteResponse)
async def calcular_frete(request: schema.FreteRequest):
    cep = request.cep.replace("-", "").strip()
    if not cep.isdigit() or len(cep) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido.")
    
    # (Sua lógica de mock de frete aqui)
    opcoes = [schema.OpcaoFrete(metodo="SEDEX", prazo_dias=3, valor=55.00)]
    return schema.FreteResponse(opcoes=opcoes)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=SERVICE_HOST, 
        port=SERVICE_PORT, 
        reload=True
    )
      
