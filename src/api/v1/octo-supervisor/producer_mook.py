''' CODIGO OBSOLETO '''
from confluent_kafka import Producer
import json, time, csv

p = Producer({'bootstrap.servers': 'localhost:8080'})

def delivery_report(err, msg):
    if err:
        print('Message delivery failed:', err)
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

with open("data.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        p.produce("raw-requests", json.dumps(row).encode("utf-8"), callback=delivery_report)
        p.flush()
        time.sleep(1)
'''---
# En tu app.py - agregar estos hooks
from src.services.traffic_analyzer import PiChatTrafficAnalyzer

# Inicializar el analizador
traffic_analyzer = PiChatTrafficAnalyzer()


'''
