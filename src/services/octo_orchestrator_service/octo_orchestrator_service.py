# octo_orchestrator_service.py - Servicio integrado
from flask import Flask, jsonify, request
import logging
import os
from datetime import datetime

# Importar módulos existentes
from elect_leader import DynamicOrchestrator
from octo_kafka_consumer import OctoOrchestratorConsumer
from octo_kafka_producer import OctoOrchestratorProducer

app = Flask(__name__)

class OctoOrchestratorService:
    """Servicio de orquestación Octo que integra todos los componentes"""
    
    def __init__(self):
        self.setup_logging()
        
        # Inicializar componentes
        self.dynamic_orchestrator = DynamicOrchestrator()
        self.kafka_producer = OctoOrchestratorProducer()
        self.kafka_consumer = OctoOrchestratorConsumer()
        
        # Integrar consumer con elect_leader
        self.kafka_consumer.integrate_with_elect_leader(self.dynamic_orchestrator)
        
        self.logger.info("🚀 Octo Orchestrator Service initialized")
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('octo-orchestrator-service')
    
    def process_input(self, input_data):
        """Procesar input a través del pipeline completo"""
        try:
            # 1. Análisis de contexto
            context_analysis = self.dynamic_orchestrator.analyze_context(input_data)
            
            # 2. Publicar análisis
            self.kafka_producer.publish_context_analysis(input_data, context_analysis)
            
            # 3. Elección de líder
            available_models = ['general_model', 'security_model', 'ethics_engine', 'technical_expert']
            leader_model, weights = self.dynamic_orchestrator.elect_leader(
                context_analysis, 
                available_models
            )
            
            # 4. Publicar resultado de elección
            routing_path = self.dynamic_orchestrator.get_routing_path(leader_model, context_analysis)
            self.kafka_producer.publish_leader_election_result(
                leader_model, weights, routing_path, context_analysis
            )
            
            # 5. Publicar métricas de salud
            self.kafka_producer.publish_health_status(
                "octo_orchestrator", 
                "healthy", 
                {"requests_processed": 1}
            )
            
            return {
                "status": "processed",
                "leader_model": leader_model,
                "weights": weights,
                "routing_path": routing_path,
                "context_analysis": context_analysis
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error processing input: {e}")
            return {"status": "error", "message": str(e)}

# Inicializar servicio
orchestrator_service = OctoOrchestratorService()

# Endpoints Flask
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "octo_orchestrator",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/process', methods=['POST'])
def process_input():
    data = request.get_json()
    input_text = data.get('input', '')
    
    result = orchestrator_service.process_input(input_text)
    return jsonify(result)

@app.route('/analyze_context', methods=['POST'])
def analyze_context():
    data = request.get_json()
    input_text = data.get('input', '')
    
    analysis = orchestrator_service.dynamic_orchestrator.analyze_context(input_text)
    return jsonify(analysis)

@app.route('/elect_leader', methods=['POST'])
def elect_leader():
    data = request.get_json()
    input_text = data.get('input', '')
    available_models = data.get('available_models', ['general_model'])
    
    context_analysis = orchestrator_service.dynamic_orchestrator.analyze_context(input_text)
    leader_model, weights = orchestrator_service.dynamic_orchestrator.elect_leader(
        context_analysis, available_models
    )
    
    return jsonify({
        "leader_model": leader_model,
        "weights": weights,
        "routing_path": orchestrator_service.dynamic_orchestrator.get_routing_path(leader_model, context_analysis)
    })

@app.route('/send_kafka_test', methods=['POST'])
def send_kafka_test():
    """Endpoint para testing de Kafka"""
    data = request.get_json()
    topic = data.get('topic', 'octo_messages')
    message = data.get('message', {})
    
    success = orchestrator_service.kafka_producer.publish_message(topic, message)
    return jsonify({"message_sent": success})

if __name__ == '__main__':
    # Iniciar consumer de Kafka
    orchestrator_service.kafka_consumer.subscribe_to_topics([
        'agi_logs',
        'avalanche_metrics',
        'octo_messages',
        'prediction_requests',
        'leader_elections'
    ])
    orchestrator_service.kafka_consumer.start_consuming()
    
    # Iniciar servidor Flask
    orchestrator_service.logger.info("🌐 Starting Flask server on port 5004")
    app.run(host='0.0.0.0', port=5004, debug=False)
