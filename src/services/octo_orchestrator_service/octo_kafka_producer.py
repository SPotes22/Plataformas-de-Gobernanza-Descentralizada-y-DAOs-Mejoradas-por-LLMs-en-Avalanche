# octo_kafka_producer.py
from confluent_kafka import Producer
import json
import logging
import os
from datetime import datetime

class OctoKafkaProducer:
    """Producer del módulo Octo para Confluent Kafka"""
    
    def __init__(self, bootstrap_servers=None):
        self.bootstrap_servers = bootstrap_servers or os.getenv('KAFKA_BROKER', 'localhost:9092')
        
        # Configuración del producer
        self.conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'octo-producer',
            'acks': 'all',
            'retries': 3,
            'compression.type': 'gzip'
        }
        
        self.producer = Producer(self.conf)
        self.setup_logging()
    
    def setup_logging(self):
        """Configurar logging para el producer"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('octo-producer')
    
    def delivery_report(self, err, msg):
        """Callback para reporte de entrega de mensajes"""
        if err is not None:
            self.logger.error(f'❌ Message delivery failed: {err}')
        else:
            self.logger.info(f'✅ Message delivered to {msg.topic()} [{msg.partition()}]')
    
    def publish_message(self, topic, message_data):
        """Publicar mensaje en topic específico"""
        try:
            # Añadir timestamp si no existe
            if 'timestamp' not in message_data:
                message_data['timestamp'] = datetime.now().isoformat()
            
            # Serializar mensaje
            message_json = json.dumps(message_data)
            
            # Publicar mensaje
            self.producer.produce(
                topic,
                value=message_json.encode('utf-8'),
                callback=self.delivery_report
            )
            
            # Flush para entrega inmediata
            self.producer.flush()
            
            self.logger.info(f"📤 Message published to {topic}: {message_data.get('type', 'unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error publishing message: {e}")
            return False
    
    def publish_agi_log(self, log_type, message, additional_data=None):
        """Publicar log del sistema AGI"""
        log_message = {
            "type": "agi_log",
            "log_type": log_type,
            "message": message,
            "source": "octo_orchestrator",
            "additional_data": additional_data or {}
        }
        
        return self.publish_message('agi_logs', log_message)
    
    def publish_avalanche_metric(self, node_type, metrics):
        """Publicar métrica de Avalanche"""
        metric_message = {
            "type": "avalanche_metric",
            "node_type": node_type,
            "metrics": metrics,
            "source": "octo_monitor"
        }
        
        return self.publish_message('avalanche_metrics', metric_message)
    
    def publish_octo_message(self, message_type, payload):
        """Publicar mensaje interno del módulo Octo"""
        octo_message = {
            "type": "octo_internal",
            "message_type": message_type,
            "payload": payload,
            "source": "octo_orchestrator"
        }
        
        return self.publish_message('octo_messages', octo_message)
    
    def publish_prediction_request(self, input_data, available_models=None):
        """Publicar solicitud de predicción"""
        prediction_request = {
            "type": "prediction_request",
            "input_data": input_data,
            "available_models": available_models or ['general_model', 'security_model'],
            "timestamp": datetime.now().isoformat()
        }
        
        return self.publish_message('prediction_requests', prediction_request)
    
    def publish_leader_election_result(self, leader_model, weights, routing_path, context_analysis):
        """Publicar resultado de elección de líder"""
        election_result = {
            "type": "leader_election",
            "leader_model": leader_model,
            "weights": weights,
            "routing_path": routing_path,
            "context_analysis": context_analysis,
            "election_timestamp": datetime.now().isoformat()
        }
        
        return self.publish_message('leader_elections', election_result)
    
    def publish_alert(self, alert_type, severity, description, source_data=None):
        """Publicar alerta del sistema"""
        alert_message = {
            "type": "system_alert",
            "alert_type": alert_type,
            "severity": severity,  # low, medium, high, critical
            "description": description,
            "source_data": source_data or {},
            "alert_timestamp": datetime.now().isoformat()
        }
        
        return self.publish_message('system_alerts', alert_message)
    
    def publish_health_status(self, service_name, status, metrics=None):
        """Publicar estado de salud del servicio"""
        health_message = {
            "type": "health_status",
            "service_name": service_name,
            "status": status,  # healthy, degraded, unhealthy
            "metrics": metrics or {},
            "check_timestamp": datetime.now().isoformat()
        }
        
        return self.publish_message('health_status', health_message)

# Integración con el sistema existente
class OctoOrchestratorProducer(OctoKafkaProducer):
    """Producer especializado para orquestación Octo"""
    
    def __init__(self):
        super().__init__()
        self.logger.info("🚀 Octo Orchestrator Producer initialized")
    
    def publish_context_analysis(self, input_data, analysis_result):
        """Publicar análisis de contexto"""
        context_message = {
            "type": "context_analysis",
            "input_data": input_data,
            "analysis_result": analysis_result,
            "analyzed_at": datetime.now().isoformat()
        }
        
        return self.publish_message('context_analysis', context_message)
    
    def publish_threat_detection(self, threat_level, detected_indicators, input_sample):
        """Publicar detección de amenazas"""
        threat_message = {
            "type": "threat_detection",
            "threat_level": threat_level,
            "detected_indicators": detected_indicators,
            "input_sample": input_sample,
            "detected_at": datetime.now().isoformat()
        }
        
        return self.publish_message('threat_detections', threat_message)
    
    def publish_ethical_analysis(self, complexity_score, ethical_indicators, recommendation):
        """Publicar análisis ético"""
        ethical_message = {
            "type": "ethical_analysis",
            "complexity_score": complexity_score,
            "ethical_indicators": ethical_indicators,
            "recommendation": recommendation,
            "analyzed_at": datetime.now().isoformat()
        }
        
        return self.publish_message('ethical_analysis', ethical_message)

# Ejemplo de uso integrado
if __name__ == "__main__":
    # Crear producer
    producer = OctoOrchestratorProducer()
    
    # Ejemplos de publicación
    producer.publish_agi_log("info", "Octo orchestrator started successfully")
    
    producer.publish_avalanche_metric("secure_node", {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "network_latency": 120
    })
    
    producer.publish_prediction_request(
        "¿Cómo funciona el mecanismo de atención en transformers?",
        ["general_model", "technical_expert"]
    )
    
    producer.publish_health_status("octo_orchestrator", "healthy", {
        "uptime": "2 hours",
        "messages_processed": 150,
        "error_rate": 0.02
    })