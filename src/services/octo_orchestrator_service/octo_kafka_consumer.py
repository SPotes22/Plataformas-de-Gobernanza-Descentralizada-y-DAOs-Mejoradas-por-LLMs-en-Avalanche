# octo_kafka_consumer.py - REFACTORED & FIXED
from confluent_kafka import Consumer, KafkaError
import json
import logging
import threading
import time
import os
from datetime import datetime

class OctoKafkaConsumer:
    """Consumer del módulo Octo - Versión Refactorizada"""
    
    def __init__(self, bootstrap_servers=None, group_id='octo-orchestrator'):
        self.bootstrap_servers = bootstrap_servers or os.getenv('KAFKA_BROKER', 'kafka:9092')
        self.group_id = group_id
        self.running = False
        self.consumer = None
        self.callbacks = {}
        
        # Configuración optimizada
        self.conf = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # Commit manual
            'session.timeout.ms': 10000,
            'max.poll.interval.ms': 300000
        }
        
        self.setup_logging()
        self.logger.info(f"🚀 Octo Consumer initialized for {self.bootstrap_servers}")
    
    def setup_logging(self):
        """Configurar logging simplificado"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('octo-consumer')
    
    def subscribe_to_topics(self, topics):
        """Suscribirse a topics con manejo de errores"""
        try:
            self.consumer = Consumer(self.conf)
            self.consumer.subscribe(topics)
            self.logger.info(f"✅ Subscribed to: {topics}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Subscription failed: {e}")
            return False
    
    def register_callback(self, topic, callback_function):
        """Registrar callback para topic específico"""
        self.callbacks[topic] = callback_function
        self.logger.info(f"📝 Callback registered for: {topic}")
    
    def process_message(self, msg):
        """Procesar mensaje de forma robusta"""
        try:
            if not msg.value():
                return
                
            topic = msg.topic()
            message_data = json.loads(msg.value().decode('utf-8'))
            
            self.logger.info(f"📨 {topic}: {message_data.get('type', 'unknown')}")
            
            # Ejecutar callback o handler por defecto
            if topic in self.callbacks:
                self.callbacks[topic](message_data)
            else:
                self.default_message_handler(topic, message_data)
            
            # ✅ FIXED: Commit sin parámetro problemático
            self.consumer.commit(message=msg)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON error: {e}")
        except Exception as e:
            self.logger.error(f"❌ Processing error: {e}")
    
    def default_message_handler(self, topic, message_data):
        """Manejador por defecto optimizado"""
        # Mapeo directo de topics a handlers
        handler_map = {
            'agi_logs': self.handle_agi_logs,
            'avalanche_metrics': self.handle_avalanche_metrics,
            'octo_messages': self.handle_octo_messages
        }
        
        handler = handler_map.get(topic, self.generic_handler)
        handler(message_data)
    
    def handle_agi_logs(self, message_data):
        """Manejador para logs AGI"""
        log_type = message_data.get('log_type', 'info')
        message = message_data.get('message', '')
        
        self.logger.info(f"🧠 AGI [{log_type}]: {message[:100]}...")
        
        # Detectar amenazas automáticamente
        threat_keywords = ['threat', 'security', 'attack', 'malicious', 'injection']
        if any(keyword in message.lower() for keyword in threat_keywords):
            self.escalate_to_security(message_data)
    
    def handle_avalanche_metrics(self, message_data):
        """Manejador para métricas de Avalanche"""
        node_type = message_data.get('node_type', 'unknown')
        metrics = message_data.get('metrics', {})
        
        self.logger.info(f"⛓️ {node_type} node - CPU: {metrics.get('cpu_usage', 'N/A')}%")
        
        # Chequear salud del nodo
        if self.is_node_unhealthy(metrics):
            self.trigger_node_alert(node_type, metrics)
    
    def handle_octo_messages(self, message_data):
        """Manejador para mensajes Octo internos"""
        msg_type = message_data.get('message_type', 'unknown')
        payload = message_data.get('payload', {})
        
        self.logger.info(f"🐙 Octo [{msg_type}]: {len(str(payload))} bytes")
        
        # Routing automático basado en tipo
        self.auto_route_message(msg_type, payload)
    
    def generic_handler(self, message_data):
        """Manejador genérico para cualquier topic"""
        self.logger.info(f"🔧 Generic handler: {message_data.get('type', 'unknown')}")
    
    def is_node_unhealthy(self, metrics):
        """Verificar si el nodo tiene problemas"""
        cpu_usage = metrics.get('cpu_usage', 0)
        memory_usage = metrics.get('memory_usage', 0)
        
        return cpu_usage > 90 or memory_usage > 85
    
    def trigger_node_alert(self, node_type, metrics):
        """Activar alerta por nodo problemático"""
        self.logger.warning(f"🚨 {node_type} node unhealthy: {metrics}")
        
        alert_data = {
            "alert_type": "node_unhealthy",
            "node_type": node_type,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # En producción, aquí se publicaría a un topic de alertas
        self.logger.info(f"📢 Alert would be sent: {alert_data}")
    
    def escalate_to_security(self, message_data):
        """Escalar problema de seguridad"""
        self.logger.warning(f"🛡️ Security escalation: {message_data.get('message')}")
    
    def auto_route_message(self, msg_type, payload):
        """Enrutamiento automático de mensajes Octo"""
        routing_table = {
            'prediction_request': 'prediction_service',
            'model_update': 'model_manager', 
            'health_check': 'health_monitor',
            'vector_update': 'vector_space'
        }
        
        destination = routing_table.get(msg_type, 'default_processor')
        self.logger.info(f"🔄 Routing {msg_type} -> {destination}")
    
    def start_consuming(self):
        """Iniciar consumo en hilo separado"""
        if not self.consumer:
            self.logger.error("❌ Consumer not initialized")
            return
        
        self.running = True
        
        def consumption_loop():
            self.logger.info("🔄 Starting consumption loop")
            
            while self.running:
                try:
                    msg = self.consumer.poll(1.0)
                    
                    if msg is None:
                        continue
                        
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            continue
                        self.logger.error(f"❌ Kafka error: {msg.error()}")
                        continue
                    
                    self.process_message(msg)
                    
                except Exception as e:
                    self.logger.error(f"❌ Loop error: {e}")
                    time.sleep(5)  # Backoff en errores
        
        # Iniciar hilo
        self.thread = threading.Thread(target=consumption_loop, daemon=True)
        self.thread.start()
        self.logger.info("✅ Consumption started")
    
    def stop_consuming(self):
        """Detener consumo gracefulmente"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        self.logger.info("🛑 Consumer stopped")

# Versión simplificada para uso directo
class SimpleOctoConsumer(OctoKafkaConsumer):
    """Consumer simplificado para deployment rápido"""
    
    def __init__(self):
        super().__init__()
        self.default_topics = ['agi_logs', 'avalanche_metrics', 'octo_messages']
    
    def start_simple(self):
        """Inicio simplificado con configuración por defecto"""
        if self.subscribe_to_topics(self.default_topics):
            self.logger.info("🚀 Simple consumer starting...")
            self.start_consuming()
            return True
        return False

# Punto de entrada principal
if __name__ == "__main__":
    consumer = OctoKafkaConsumer()
    
    if consumer.start_simple():
        consumer.logger.info("🎯 Consumer running. Press Ctrl+C to stop.")
        try:
            # Mantener vivo
            while True:
                time.sleep(10)
                consumer.logger.info("💓 Consumer heartbeat")
        except KeyboardInterrupt:
            consumer.stop_consuming()
            consumer.logger.info("👋 Consumer stopped by user")
    else:
        consumer.logger.error("💥 Failed to start consumer")