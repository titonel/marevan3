# Usa uma imagem oficial do Python leve
FROM python:3.11-slim

# Define variáveis de ambiente para o Python não gerar arquivos .pyc e não usar buffer no log
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para o SQLite e bibliotecas Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências e instala
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . /app/

# Expõe a porta que o Django usa
EXPOSE 8000

# Comando para rodar as migrações e iniciar o servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]