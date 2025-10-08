# octo-module-1.py - Microservicio Octo Supervisor
from flask import Flask, request, jsonify
import json
import hashlib
import hmac
import numpy as np
from datetime import datetime
from confluent_kafka import Consumer, Producer
import joblib
import os
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('octo-supervisor')

# ===== HOTFIX: Auto Lockout Vector Space =====
class EntropicVectorSpace:
    def __init__(self):
        self.dimensions = ['qué', 'por_qué', 'para_qué', 'cómo', 'cuándo', 'dónde']
        self.vector_length = 128
        self.matrix = []
    
    def add_script_vector(self, script_data: dict):
        vector = []
        for dim in self.dimensions:
            text = script_data.get(dim, '')
            hash_obj = hashlib.sha256(text.encode())
            hex_digest = hash_obj.hexdigest()[:self.vector_length]
            vector.append(hex_digest)
        self.matrix.append(vector)
        return vector

# ===== OCTO KAFKA MODULE =====
class OctoKafkaProducer:
    def __init__(self, bootstrap_servers=os.getenv('KAFKA_BROKER', 'kafka:9092')):
        self.conf = {'bootstrap.servers': bootstrap_servers}
        self.producer = Producer(self.conf)
    
    def send_octo_message(self, topic: str, message: dict):
        try:
            self.producer.produce(topic, json.dumps(message).encode('utf-8'))
            self.producer.flush()
            logger.info(f"Message sent to topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Kafka producer error: {e}")
            return False

class OctoKafkaConsumer:
    def __init__(self, bootstrap_servers=os.getenv('KAFKA_BROKER', 'kafka:9092'), 
                 group_id=os.getenv('OCTO_GROUP', 'octo-supervisor')):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.conf)
    
    def subscribe_octo_topic(self, topic: str):
        self.consumer.subscribe([topic])
    
    def poll_octo_messages(self, timeout=1.0):
        return self.consumer.poll(timeout)

# ===== OCTO ENDPOINTS MODULE =====
class ModularWarriorEndpoints:
    def __init__(self, models_dir='./secrets/models/compressed/'):
        self.models_dir = models_dir
        self.loaded_models = {}
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.82))
    
    def safe_prediction(self, features: list) -> dict:
        if len(self.loaded_models) == 0:
            return {"error": "No models loaded"}
        
        model_name = list(self.loaded_models.keys())[0]
        model = self.loaded_models[model_name]
        
        try:
            prediction = model.predict_proba([features])[0]
            confidence = max(prediction)
            
            if confidence >= self.confidence_threshold:
                return {
                    "prediction": int(np.argmax(prediction)),
                    "confidence": float(confidence),
                    "status": "safe"
                }
            else:
                self._escalate_low_confidence(confidence, features)
                return {
                    "prediction": None,
                    "confidence": float(confidence),
                    "status": "escalated"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def load_model(self, model_filename: str):
        model_path = os.path.join(self.models_dir, model_filename)
        try:
            model = joblib.load(model_path)
            self.loaded_models[model_filename] = model
            logger.info(f"Model {model_filename} loaded successfully")
            return {"status": f"Model {model_filename} loaded successfully"}
        except Exception as e:
            logger.error(f"Model loading error: {e}")
            return {"error": str(e)}
    
    def export_model(self, model_name: str, format_type: str):
        if model_name not in self.loaded_models:
            return {"error": "Model not loaded"}
        
        if format_type == 'pkl':
            return {"format": "pkl", "status": "export_ready"}
        elif format_type == 'npy':
            return {"format": "npy", "status": "matrix_export_ready"}
        else:
            return {"error": "Unsupported format"}
    
    def scan_modules(self):
        return {
            "available_modules": ["kafka", "tools", "endpoints", "security"],
            "status": "operational"
        }
    
    def health_check(self):
        return {
            "last_endpoint": "safe_prediction",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    def _escalate_low_confidence(self, confidence: float, features: list):
        log_entry = {
            "confidence": confidence,
            "features": features[:5],
            "timestamp": datetime.now().isoformat(),
            "action": "escalated_to_admin"
        }
        os.makedirs('/app/admin/dashboard/actions', exist_ok=True)
        with open('/app/admin/dashboard/actions/low_confidence_log.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        logger.warning(f"Low confidence escalated: {confidence}")

# ===== INICIALIZACIÓN =====
vector_space = EntropicVectorSpace()
kafka_producer = OctoKafkaProducer()
endpoints = ModularWarriorEndpoints()

# ===== ENDPOINTS FLASK =====
@app.route('/health', methods=['GET'])
def health():
    return jsonify(endpoints.health_check())

@app.route('/safe_prediction', methods=['POST'])
def safe_prediction():
    data = request.get_json()
    features = data.get('features', [])
    result = endpoints.safe_prediction(features)
    return jsonify(result)

@app.route('/load_model', methods=['POST'])
def load_model():
    data = request.get_json()
    model_filename = data.get('model_filename')
    result = endpoints.load_model(model_filename)
    return jsonify(result)

@app.route('/export_model', methods=['POST'])
def export_model():
    data = request.get_json()
    model_name = data.get('model_name')
    format_type = data.get('format_type', 'pkl')
    result = endpoints.export_model(model_name, format_type)
    return jsonify(result)

@app.route('/scan_modules', methods=['GET'])
def scan_modules():
    return jsonify(endpoints.scan_modules())

@app.route('/add_vector', methods=['POST'])
def add_vector():
    data = request.get_json()
    vector = vector_space.add_script_vector(data)
    return jsonify({"vector_added": True, "dimensions": len(vector)})

@app.route('/send_kafka', methods=['POST'])
def send_kafka():
    data = request.get_json()
    topic = data.get('topic', 'octo-messages')
    message = data.get('message', {})
    success = kafka_producer.send_octo_message(topic, message)
    return jsonify({"message_sent": success})

if __name__ == '__main__':
    logger.info("🚀 Starting Octo Supervisor Microservice on port 5003")
    app.run(host='0.0.0.0', port=5003, debug=False)
