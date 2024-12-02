import time
from kafka_folder.producer import enviar_para_kafka
from extracao.extracao_clima import obter_dados_climaticos

if __name__ == "__main__":
    while True:
        try:
            # Obter dados climáticos
            dados_climaticos = obter_dados_climaticos()
            if dados_climaticos:
                # Enviar cada dado individualmente
                for dado in dados_climaticos:
                    enviar_para_kafka(dado)
            else:
                print("Nenhum dado retornado pela API.")

            # Aguardar antes de buscar novos dados
            time.sleep(5)  # Ajuste o intervalo conforme necessário
        except Exception as e:
            print(f"Erro no loop principal: {e}")
            time.sleep(10)  # Aguardar antes de tentar novamente
