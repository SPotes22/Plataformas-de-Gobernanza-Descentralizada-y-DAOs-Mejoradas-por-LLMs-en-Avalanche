#!/usr/bin/env python3
"""
Kafka Producer con confluent-kafka - HIGH PERFORMANCE
Entropía: 2.85%
"""
import time
import json
import logging
from confluent_kafka import Producer
from confluent_kafka import KafkaError
import subprocess as sp
from datetime import datetime

class AvalancheKafkaProducer:
    def __init__(self, node_name, node_type, kafka_broker='kafka:9092'):
        self.node_name = node_name
        self.node_type = node_type
        self.setup_logging()
        
        # Configurar Kafka Producer (confluent-kafka)
        self.producer = Producer({
            'bootstrap.servers': kafka_broker,
            'batch.size': 16384,
            'linger.ms': 10,
            'acks': 'all',
            'retries': 5,
            'compression.type': 'snappy'
        })
        
        self.topics = {
            'logs': 'avalanche_logs',
            'metrics': 'avalanche_metrics', 
            'alerts': 'avalanche_alerts'
        }
    
    def setup_logging(self):
        logging.basicConfig(
            filename=f'/app/logs/kafka_producer_{self.node_name}.log',
            level=logging.INFO,
            format='%(asctime)s | %(message)s'
        )
        self.log = logging.getLogger()
        self.log.info(f"🚀 Kafka Producer (confluent) iniciado para {self.node_name}")
    
    def delivery_callback(self, err, msg):
        """Callback para confirmación de entrega"""
        if err:
            self.log.error(f"❌ Error entrega: {err}")
        else:
            self.log.info(f"📤 Enviado a {msg.topic()} | Partition: {msg.partition()}")
    
    def get_node_metrics(self):
        """Obtener métricas del nodo Avalanche"""
        try:
            # Logs recientes
            logs_cmd = f"docker logs --tail 20 {self.node_name} 2>&1"
            logs_result = sp.run(logs_cmd, shell=True, capture_output=True, text=True)
            logs = logs_result.stdout if logs_result.returncode == 0 else ""
            
            # Estado del contenedor
            status_cmd = f"docker ps -f name={self.node_name} --format json"
            status_result = sp.run(status_cmd, shell=True, capture_output=True, text=True)
            
            status = {}
            if status_result.returncode == 0 and status_result.stdout.strip():
                status = json.loads(status_result.stdout)
            
            return {
                'node_name': self.node_name,
                'node_type': self.node_type,
                'timestamp': datetime.now().isoformat(),
                'logs': logs,
                'status': status,
                'health': self.check_health()
            }
        except Exception as e:
            return {
                'node_name': self.node_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_health(self):
        """Verificar salud del nodo"""
        try:
            health_cmd = f"curl -s http://localhost:9650/ext/health"
            result = sp.run(health_cmd, shell=True, capture_output=True, text=True)
            return {'healthy': result.returncode == 0, 'response': result.stdout[:100]}
        except:
            return {'healthy': False, 'response': 'health_check_failed'}
    
    def send_to_kafka(self, data, topic_type):
        """Enviar datos a Kafka (HIGH PERFORMANCE)"""
        try:
            topic = self.topics[topic_type]
            self.producer.produce(
                topic,
                value=json.dumps(data).encode('utf-8'),
                callback=self.delivery_callback
            )
            self.producer.poll(0)  # Servir callbacks de entrega
            return True
        except Exception as e:
            self.log.error(f"❌ Error Kafka: {e} | Topic: {topic}")
            return False
    
    def produce_loop(self):
        """Loop principal de producción (HIGH PERFORMANCE)"""
        while True:
            try:
                # 1. Recopilar métricas
                metrics = self.get_node_metrics()
                
                # 2. Enviar logs a Kafka
                if metrics.get('logs'):
                    self.send_to_kafka(metrics, 'logs')
                
                # 3. Enviar métricas a Kafka  
                self.send_to_kafka(metrics, 'metrics')
                
                # 4. Enviar alertas si es necesario
                if metrics.get('error') or not metrics.get('health', {}).get('healthy'):
                    alert_data = {
                        'node': self.node_name,
                        'type': 'health_alert',
                        'message': 'Node health issue',
                        'timestamp': datetime.now().isoformat()
                    }
                    self.send_to_kafka(alert_data, 'alerts')
                
                # 5. Flush periódico para máxima performance
                if int(time.time()) % 30 == 0:
                    self.producer.flush()
                
                time.sleep(5)  # Envío cada 5 segundos (MÁS RÁPIDO)
                
            except Exception as e:
                self.log.error(f"🔧 Error en producción: {e}")
                time.sleep(10)

def main():
    import os
    node_name = os.getenv('NODE_NAME', 'avalanche_node_secure')
    node_type = os.getenv('NODE_TYPE', 'secure')
    
    producer = AvalancheKafkaProducer(node_name, node_type)
    producer.produce_loop()

if __name__ == "__main__":
    main()
