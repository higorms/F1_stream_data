from kafka_.producer import enviar_para_kafka
from extracao.extracao_clima import obter_dados_climaticos


enviar_para_kafka(
    obter_dados_climaticos()
)