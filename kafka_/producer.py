from kafka import KafkaProducer
from extracao.extracao_clima import obter_dados_climaticos
import json
import time
import os

# Carregar configurações do arquivo JSON
with open(os.path.join(os.path.dirname(__file__), 'configs_kafka.json')) as f:
    kafka_config = json.load(f)


# Inicializar o Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=kafka_config['bootstrap_servers'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def enviar_para_kafka(dados):
    """Envia os dados para o Kafka."""
    try:
        producer.send(kafka_config['topic'], value=dados)
        producer.flush()
        print(f"Dados enviados para o Kafka com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar para o Kafka: {e}")


if __name__ == "__main__":
    while True:
        # Obter dados climáticos
        dados_climaticos = obter_dados_climaticos()
        if dados_climaticos:
            enviar_para_kafka(dados_climaticos)

        # Aguardar antes de buscar novos dados
        time.sleep(60)  # Ajuste o intervalo conforme necessário

