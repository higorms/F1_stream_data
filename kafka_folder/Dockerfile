FROM python:3.9-slim

WORKDIR /app

# Copiar apenas os arquivos necessários do kafka_folder
COPY kafka_folder/producer.py /app/
COPY requirements.txt /app/
COPY entrypoint_fluxo_clima.py /app/

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Comando permanece apontando para o arquivo na raiz
CMD ["python", "entrypoint_fluxo_clima.py"]