# Estágio 1: Build (Construção)
# --- CORREÇÃO AQUI ---
# Atualiza a versão do Node para uma compatível com o Vite 7
FROM node:20-alpine AS build
# O contexto é 'frontend/'
WORKDIR /app

# --- CORREÇÃO ---
# Diz ao Docker para olhar DENTRO da pasta app-ecommerce
COPY app-ecommerce/package.json .
COPY app-ecommerce/package-lock.json .

# Instala as dependências
RUN npm ci

# --- CORREÇÃO ---
# Copia o resto do código de 'app-ecommerce' para a raiz
COPY app-ecommerce/ .

# O 'index.html' e 'vite.config.ts' etc. estão agora em /app
# e o 'vite build' vai encontrá-los
RUN npx vite build

# Estágio 2: Serve (Servidor Estático)
FROM nginx:1.25-alpine
# O build (dist) está em /app/dist
COPY --from=build /app/dist /usr/share/nginx/html

# O nginx.conf está no contexto 'frontend/', então isto está correto
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 5173

