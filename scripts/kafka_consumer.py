#!/usr/bin/env python3
"""
Kafka Consumer con confluent-kafka - HIGH PERFORMANCE
Entropía: 2.87%
"""
import json
import logging
from confluent_kafka import Consumer, KafkaError
from datetime import datetime

class AvalancheOrchestrator:
    def __init__(self, group_id, mode='load_balancing'):
        self.group_id = group_id
        self.mode = mode
        self.setup_logging()
        
        # Configurar Kafka Consumer (confluent-kafka)
        self.consumer = Consumer({
            'bootstrap.servers': 'kafka:9092',
            'group.id': group_id,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
            'max.poll.interval.ms': 300000
        })
        
        self.consumer.subscribe(['avalanche_logs', 'avalanche_metrics', 'avalanche_alerts'])
        
        self.node_stats = {}
        self.injection_patterns = [
            r"'.*;.*--", r"union.*select", r"block_id=.*[;&|]",
            r"0x[0-9a-f]{64}.*[;'\"]", r"'.*OR.*1=1.*block"
        ]
    
    def setup_logging(self):
        log_file = f'/app/logs/orchestrator_{self.group_id}.log'
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s'
        )
        self.log = logging.getLogger()
        self.log.info(f"🎼 Orchestrator (confluent) iniciado | Group: {self.group_id}")
    
    def detect_injections(self, log_data):
        """Detección de inyecciones en tiempo real"""
        import re
        detections = []
        
        for pattern in self.injection_patterns:
            if re.search(pattern, log_data, re.IGNORECASE):
                detections.append(pattern)
        
        return detections
    
    def update_node_stats(self, node_data):
        """Actualizar estadísticas de nodos para load balancing"""
        node_name = node_data.get('node_name')
        
        if node_name not in self.node_stats:
            self.node_stats[node_name] = {
                'message_count': 0,
                'last_seen': datetime.now(),
                'health_score': 100,
                'injection_count': 0
            }
        
        stats = self.node_stats[node_name]
        stats['message_count'] += 1
        stats['last_seen'] = datetime.now()
        
        # Detectar inyecciones
        logs = node_data.get('logs', '')
        injections = self.detect_injections(logs)
        if injections:
            stats['injection_count'] += len(injections)
            self.log.warning(f"🚨 Inyecciones en {node_name}: {injections}")
    
    def analyze_load_distribution(self):
        """Analizar distribución de carga entre nodos"""
        if not self.node_stats:
            return {}
        
        total_messages = sum(stats['message_count'] for stats in self.node_stats.values())
        load_distribution = {}
        
        for node, stats in self.node_stats.items():
            load_percent = (stats['message_count'] / total_messages * 100) if total_messages > 0 else 0
            load_distribution[node] = {
                'load_percent': round(load_percent, 2),
                'injection_ratio': stats['injection_count'] / max(stats['message_count'], 1),
                'health_score': stats['health_score']
            }
        
        return load_distribution
    
    def consume_messages(self):
        """Consumir mensajes de Kafka (HIGH PERFORMANCE)"""
        self.log.info("🎧 Iniciando consumo con confluent-kafka...")
        
        try:
            while True:
                msg = self.consumer.poll(1.0)  # Timeout de 1 segundo
                
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        self.log.error(f"❌ Kafka error: {msg.error()}")
                        continue
                
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    topic = msg.topic()
                    
                    # Procesar según el topic
                    if topic == 'avalanche_logs':
                        self.process_logs(data)
                    elif topic == 'avalanche_metrics':
                        self.process_metrics(data)
                    elif topic == 'avalanche_alerts':
                        self.process_alerts(data)
                    
                    # Log cada 50 mensajes
                    total_msgs = sum(s['message_count'] for s in self.node_stats.values())
                    if total_msgs % 50 == 0:
                        load_info = self.analyze_load_distribution()
                        self.log.info(f"📊 Load: {load_info}")
                        
                except Exception as e:
                    self.log.error(f"❌ Error procesando mensaje: {e}")
                    
        except KeyboardInterrupt:
            self.log.info("🛑 Consumer detenido")
        finally:
            self.consumer.close()
    
    def process_logs(self, data):
        """Procesar logs de nodos"""
        self.update_node_stats(data)
        
        # Análisis de inyecciones en tiempo real
        logs = data.get('logs', '')
        node_name = data.get('node_name')
        
        injections = self.detect_injections(logs)
        if injections:
            alert_msg = f"🔴 INYECCIÓN | Node: {node_name} | Patterns: {injections}"
            self.log.warning(alert_msg)
    
    def process_metrics(self, data):
        """Procesar métricas de nodos"""
        node_name = data.get('node_name')
        health = data.get('health', {})
        
        if not health.get('healthy', True):
            self.log.error(f"⚠️ Node unhealthy: {node_name}")
    
    def process_alerts(self, data):
        """Procesar alertas"""
        self.log.warning(f"🚨 ALERTA: {data}")

def main():
    import os
    group_id = os.getenv('CONSUMER_GROUP', 'orchestrator')
    mode = os.getenv('ORCHESTRATION_MODE', 'load_balancing')
    
    orchestrator = AvalancheOrchestrator(group_id, mode)
    orchestrator.consume_messages()

if __name__ == "__main__":
    main()
