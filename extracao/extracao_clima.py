from urllib.request import urlopen
import pandas as pd
import json


BASE_URL_CLIMA = "https://api.openf1.org/v1/weather"


def obter_dados_climaticos(session_key="latest"):
    # Constrói a URL com os parâmetros corretamente formatados
    url = f"{BASE_URL_CLIMA}?session_key={session_key}"
    
    try:
        response = urlopen(url)
        if response.getcode() == 200:
            data = json.loads(response.read())
            return data
        else:
            print(f"Erro ao obter dados da API: {response.getcode()}")
            return None
    except Exception as e:
        print(f"Erro ao acessar a API: {e}")
        return None


# Teste com um endpoint
if __name__ == "__main__":
    data = obter_dados_climaticos()
    if data:
        print("Dados climáticos obtidos com sucesso")  # Formatação mais legível
    else:
        print("Nenhum dado climático encontrado")