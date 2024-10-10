import streamlit as st
from lxml import etree
import plotly.express as px
import pandas as pd
import numpy as np

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

# Carregar o arquivo TCX
path_0730 = 'C:\\Users\\doniz\\Documents\\TrackYourTrack\\data\\easy_20240730.tcx'
df_0730 = load_tcx(path_0730)

path_0801 = 'C:\\Users\\doniz\\Documents\\TrackYourTrack\\data\\easy_20240801.tcx'
df_0801 = load_tcx(path_0801)

t0_0730 = df_0730['timestamp'][0]
t0_0801 = df_0801['timestamp'][0]

df_0730['t'] = (df_0730['timestamp'] - t0_0730).dt.total_seconds()
df_0801['t'] = (df_0801['timestamp'] - t0_0801).dt.total_seconds()

df = pd.merge(df_0730[['t','heart_rate','cadence']], df_0801[['t','heart_rate','cadence']], on='t', how='outer')
df = df.set_index('t')

df['heart_rate_x'] = df['heart_rate_x'].interpolate(method='linear', limit_direction='both')
df['heart_rate_y'] = df['heart_rate_y'].interpolate(method='linear', limit_direction='both')

df['cadence_x'] = df['cadence_x'].interpolate(method='linear', limit_direction='both')
df['cadence_y'] = df['cadence_y'].interpolate(method='linear', limit_direction='both')

st.write("""
# Teste e mais teste
""")

st.line_chart(df[['heart_rate_x','heart_rate_y']])
st.line_chart(df[['cadence_x','cadence_y']])