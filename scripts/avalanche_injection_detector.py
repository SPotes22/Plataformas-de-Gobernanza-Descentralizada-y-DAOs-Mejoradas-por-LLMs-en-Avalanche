#!/usr/bin/env python3
"""
avalanche_injection_detector.py
Entropía: 2.92% | Complejidad: 4
Detección de inyecciones block_id + Training Data Generation
"""
import time
import logging
import subprocess as sp
import json
import math
import re
from datetime import datetime
from pathlib import Path

class BlockInjectionDetector:
    def __init__(self, mode="training"):
        self.secure_node = "avalanche_node_secure"
        self.vulnerable_node = "avalanche_node_vulnerable"
        self.interval = 30
        self.max_entropy = 3.14
        self.mode = mode
        self.detection_threshold = 0.85
        
        # Inicializar directorios
        self.setup_directories()
        self.setup_logging()
        self.injection_patterns = self.load_injection_patterns()
    
    def setup_directories(self):
        """Crear directorios para training data"""
        Path("training_data").mkdir(exist_ok=True)
        Path("injection_patterns").mkdir(exist_ok=True)
        Path("detection_logs").mkdir(exist_ok=True)
    
    def setup_logging(self):
        """Configurar logging de detección"""
        log_file = "detection_logs/injection_detector.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.log = logging.getLogger()
        self.log.info(f"🔍 Block Injection Detector iniciado - Modo: {self.mode}")
    
    def load_injection_patterns(self):
        """Cargar patrones de inyección específicos para blockchain"""
        patterns = {
            'block_id_injection': [
                r"block[_\-]?id=.*[;&|]",                    # Inyección en parámetros
                r"0x[0-9a-f]{64}.*[;'\"]",                   # Block hashes manipulados
                r"'.*OR.*1=1.*block",                        # SQL injection en block
                r"block.*drop.*table",                       # Drop table targeting blocks
                r"block.*union.*select",                     # Union select en blocks
                r"'.*;.*--.*block",                          # Comment injection
                r"block.*<script>",                          # XSS targeting blocks
                r"block_id.*%.*%",                           # LIKE injection patterns
            ],
            'rpc_injection': [
                r"\"method\":\s*\"[^\"].*[;{]",              # JSON-RPC method injection
                r"params.*\[.*\].*[;&]",                     # Params array injection
                r"\"jsonrpc\":\s*\"[0-9].*[^\"]",            # JSON-RPC version manipulation
            ],
            'consensus_attack': [
                r"double.*spend",                            # Double spend patterns
                r"reorg.*attack",                            # Chain reorganization
                r"51%.*attack",                              # Majority attack
                r"sybil.*attack",                            # Sybil attack patterns
            ]
        }
        
        # Guardar patrones para auditoría
        patterns_file = "injection_patterns/blockchain_patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)
            
        return patterns
    
    def get_node_metrics(self, node_name):
        """Obtener métricas completas del nodo"""
        try:
            # Logs
            logs_cmd = f"docker logs --tail 50 {node_name} 2>&1"
            logs_result = sp.run(logs_cmd, shell=True, capture_output=True, text=True)
            logs = logs_result.stdout if logs_result.returncode == 0 else ""
            
            # Estado del contenedor
            status_cmd = f"docker ps -f name={node_name} --format json"
            status_result = sp.run(status_cmd, shell=True, capture_output=True, text=True)
            
            status = {}
            if status_result.returncode == 0 and status_result.stdout.strip():
                status = json.loads(status_result.stdout)
            
            return {
                'logs': logs,
                'status': status,
                'entropy': self.calculate_entropy(logs),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.log.error(f"Error obteniendo métricas de {node_name}: {e}")
            return {'logs': '', 'status': {}, 'entropy': 0.0, 'error': str(e)}
    
    def calculate_entropy(self, text):
        """Calcular entropía del texto"""
        if not text or len(text) < 10:
            return 0.0
            
        freq = {}
        for char in text[:8192]:  # Mayor sample para mejor análisis
            freq[char] = freq.get(char, 0) + 1
            
        total_chars = len(text)
        entropy = 0.0
        
        for count in freq.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
                
        return min(entropy, self.max_entropy)
    
    def detect_injections(self, logs):
        """Detectar patrones de inyección en logs"""
        detections = {}
        
        for pattern_type, patterns in self.injection_patterns.items():
            detections[pattern_type] = {}
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, logs, re.IGNORECASE)
                if matches:
                    detections[pattern_type][f"pattern_{i}"] = {
                        'matches': matches,
                        'count': len(matches),
                        'pattern': pattern
                    }
        
        return detections
    
    def analyze_nodes_comparison(self):
        """Análisis comparativo entre nodo seguro y vulnerable"""
        # Métricas del nodo seguro
        secure_metrics = self.get_node_metrics(self.secure_node)
        secure_detections = self.detect_injections(secure_metrics['logs'])
        
        # Métricas del nodo vulnerable  
        vulnerable_metrics = self.get_node_metrics(self.vulnerable_node)
        vulnerable_detections = self.detect_injections(vulnerable_metrics['logs'])
        
        # Análisis comparativo
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode,
            'secure_node': {
                'entropy': secure_metrics['entropy'],
                'detections': secure_detections,
                'total_detections': sum(len(v) for v in secure_detections.values()),
                'status': secure_metrics.get('status', {})
            },
            'vulnerable_node': {
                'entropy': vulnerable_metrics['entropy'],
                'detections': vulnerable_detections,
                'total_detections': sum(len(v) for v in vulnerable_detections.values()),
                'status': vulnerable_metrics.get('status', {})
            }
        }
        
        # Calcular score de anomalía
        secure_total = analysis['secure_node']['total_detections']
        vulnerable_total = analysis['vulnerable_node']['total_detections']
        
        if secure_total == 0:
            analysis['anomaly_score'] = vulnerable_total * 2.0
        else:
            analysis['anomaly_score'] = (vulnerable_total - secure_total) / secure_total
        
        return analysis
    
    def save_training_data(self, analysis):
        """Guardar data de training para el modelo ML"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"training_data/injection_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return filename
    
    def generate_alert(self, analysis):
        """Generar alertas basadas en el análisis"""
        anomaly_score = analysis['anomaly_score']
        vulnerable_detections = analysis['vulnerable_node']['total_detections']
        
        if anomaly_score > 2.0 or vulnerable_detections > 10:
            alert_level = "🔴 CRÍTICO"
        elif anomaly_score > 1.0 or vulnerable_detections > 5:
            alert_level = "🟡 ALTO"
        elif anomaly_score > 0.5 or vulnerable_detections > 2:
            alert_level = "🟠 MEDIO"
        else:
            alert_level = "🟢 NORMAL"
        
        return alert_level
    
    def run_detection_loop(self):
        """Loop principal de detección"""
        self.log.info("🕷️ Iniciando detección de inyecciones block_id")
        
        detection_count = 0
        
        while True:
            try:
                detection_count += 1
                
                # 1. Análisis comparativo
                analysis = self.analyze_nodes_comparison()
                
                # 2. Guardar training data
                training_file = self.save_training_data(analysis)
                
                # 3. Generar alerta
                alert_level = self.generate_alert(analysis)
                
                # 4. Log de resultados
                anomaly = analysis['anomaly_score']
                secure_dets = analysis['secure_node']['total_detections']
                vuln_dets = analysis['vulnerable_node']['total_detections']
                
                log_message = (
                    f"{alert_level} | Anomalía: {anomaly:.2f} | "
                    f"Secure: {secure_dets} | Vulnerable: {vuln_dets} | "
                    f"Cycle: {detection_count}"
                )
                
                if anomaly > 1.0:
                    self.log.warning(log_message)
                    self.log.info(f"💾 Training data: {training_file}")
                else:
                    self.log.info(log_message)
                
                # 5. Esperar siguiente ciclo
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                self.log.info("🛑 Detección detenida por usuario")
                break
            except Exception as e:
                self.log.error(f"❌ Error en ciclo de detección: {e}")
                time.sleep(60)  # Esperar más en caso de error

def main():
    """Función principal"""
    detector = BlockInjectionDetector(mode="training")
    detector.run_detection_loop()

if __name__ == "__main__":
    main()
