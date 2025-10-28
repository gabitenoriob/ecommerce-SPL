# Use a imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do microserviço para o contêiner
COPY . .

# Expõe a porta que o Uvicorn vai usar
# Esta porta é INTERNA do contêiner. O Traefik vai se conectar a ela.
# (Não mude isso, mesmo que os serviços usem 8001, 8002, 8003. 
# O Uvicorn no main.py define a porta real.)
EXPOSE 8000 

# Comando para rodar o app
# O main.py vai definir a porta correta (8001, 8002, ou 8003)
CMD ["python", "main.py"]