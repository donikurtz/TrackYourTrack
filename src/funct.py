from lxml import etree
import pandas as pd

def load_tcx(path):
    # Carregar o arquivo TCX
    tree = etree.parse(path)

    # Definição dos Namespaces
    ns = {
        'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'  # Adicione o URI correto para ns3
    }

    tcx_data = []

    # Extrair dados de cada ponto na trilha
    for activity in tree.xpath('//ns:Activity', namespaces=ns):
        for lap in activity.xpath('.//ns:Lap', namespaces=ns):
            for track in lap.xpath('.//ns:Track', namespaces=ns):
                for trackpoint in track.xpath('.//ns:Trackpoint', namespaces=ns):
                    # Extrair o timestamp
                    time = trackpoint.xpath('.//ns:Time', namespaces=ns)[0].text
                    
                    # Extrair informações de posição
                    latitude = trackpoint.xpath('.//ns:Position/ns:LatitudeDegrees', namespaces=ns)[0].text
                    longitude = trackpoint.xpath('.//ns:Position/ns:LongitudeDegrees', namespaces=ns)[0].text
                    
                    # Extrair altitude
                    altitude = trackpoint.xpath('.//ns:AltitudeMeters', namespaces=ns)[0].text
                    
                    # Extrair distância percorrida até o momento
                    distance = trackpoint.xpath('.//ns:DistanceMeters', namespaces=ns)[0].text
                    
                    # Extrair frequência cardíaca
                    hr = trackpoint.xpath('.//ns:HeartRateBpm/ns:Value', namespaces=ns)
                    hr_value = int(hr[0].text) if hr else None
                    
                    # Extrair cadência do namespace ns3
                    cadence = trackpoint.xpath('.//ns3:RunCadence', namespaces=ns)
                    cadence_value = int(cadence[0].text) if cadence else None
                    
                    # Extrair velocidade do namespace ns3
                    speed = trackpoint.xpath('.//ns3:Speed', namespaces=ns)
                    speed_value = float(speed[0].text) if speed else None
                    
                    # Adicionar dados ao dicionário para cada Trackpoint
                    tcx_data.append({
                        'timestamp': pd.to_datetime(time),
                        'latitude': float(latitude),
                        'longitude': float(longitude),
                        'altitude': float(altitude),
                        'distance': float(distance),
                        'heart_rate': hr_value,
                        'cadence': cadence_value,
                        'speed': speed_value
                    })

    # Converter listas em DataFrames
    tcx_df = pd.DataFrame(tcx_data)

    # Converter timestamps para garantir alinhamento
    tcx_df['timestamp'] = pd.to_datetime(tcx_df['timestamp'])

    # Converter os timestamps para o mesmo fuso horário (ou remover a informação de fuso horário)
    tcx_df['timestamp'] = tcx_df['timestamp'].dt.tz_localize(None)

    return tcx_df