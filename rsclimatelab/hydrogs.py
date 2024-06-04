import xml.etree.ElementTree as ET

import pandas as pd
import requests

BASE_URL = "https://telemetriaws1.ana.gov.br//ServiceANA.asmx"


def get_hidrometeorological_data(cod_estacao: str,
                                 data_inicio: str,
                                 data_fim: str) -> pd.DataFrame:
    # Define the URL with query parameters
    url = f"{BASE_URL}/DadosHidrometeorologicos?codEstacao={cod_estacao}" \
        f"&dataInicio={data_inicio}&dataFim={data_fim}"

    # Make the GET request to the service
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Parse the XML response
    root = ET.fromstring(response.content)

    # Initialize a list to store the records
    records = []

    # Iterate over the DadosHidrometereologicos elements and extract data
    for dados in root.findall('.//DadosHidrometereologicos'):
        record = {
            'data_hora': pd.to_datetime(dados.find('DataHora').text),  # type:ignore
            'cod_estacao': dados.find('CodEstacao').text,  # type:ignore
            'vazao': dados.find('Vazao').text,  # type:ignore
            'nivel': dados.find('Nivel').text,  # type:ignore
            'chuva': dados.find('Chuva').text,  # type:ignore
        }
        records.append(record)

    # Convert the list of records to a Pandas DataFrame
    df = pd.DataFrame(records)
    df = df.sort_values(by=["data_hora"])
    return df
