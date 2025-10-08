#!/usr/bin/env python3
"""
InjectionDetectorDaemon - Detecta inyecciones de block_id
Entropía: 2.95% | Complejidad: 4
"""
import time, logging, subprocess as sp, json, math, re
from datetime import datetime

class InjectionDetector:
    def __init__(self):
        self.secure_node = "avalanche_node_secure"
        self.vulnerable_node = "avalanche_node_vulnerable" 
        self.interval = 30
        self.max_entropy = 3.14
        self.injection_patterns = self._load_injection_patterns()
        self.setup_logging()
    
    def _load_injection_patterns(self):
        """Patrones de inyección de block_id para training"""
        return {
            'sql_injection': [r"'.*;.*--", r"union.*select", r"drop.*table"],
            'block_id_injection': [r"0x[0-9a-f]{64}", r"block_id=.*[;&|]", r"'.*OR.*1=1"],
            'rpc_injection': [r"\"method\":\s*\"[^\"].*[;{]", r"params.*\[.*\].*[;&]"],
            'json_injection': [r"\".*\":\s*\".*[}{].*\""]
        }
    
    def setup_logging(self):
        logging.basicConfig(
            filename='/app/training_data/detection.log',
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s'
        )
        self.log = logging.getLogger()
    
    def get_node_logs(self, node_name, lines=100):
        """Obtiene logs de un nodo específico"""
        try:
            cmd = f"docker logs --tail {lines} {node_name} 2>&1"
            result = sp.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except:
            return ""
    
    def detect_injection_patterns(self, logs):
        """Detecta patrones de inyección en los logs"""
        detections = {}
        
        for pattern_type, patterns in self.injection_patterns.items():
            detections[pattern_type] = []
            for pattern in patterns:
                matches = re.findall(pattern, logs, re.IGNORECASE)
                if matches:
                    detections[pattern_type].extend(matches)
        
        return detections
    
    def compare_node_behaviors(self):
        """Compara comportamiento entre nodo seguro y vulnerable"""
        secure_logs = self.get_node_logs(self.secure_node)
        vulnerable_logs = self.get_node_logs(self.vulnerable_node)
        
        secure_detections = self.detect_injection_patterns(secure_logs)
        vulnerable_detections = self.detect_injection_patterns(vulnerable_logs)
        
        # Análisis comparativo
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'secure_node': {
                'log_entropy': self.calculate_entropy(secure_logs),
                'detections': secure_detections,
                'total_detections': sum(len(v) for v in secure_detections.values())
            },
            'vulnerable_node': {
                'log_entropy': self.calculate_entropy(vulnerable_logs),
                'detections': vulnerable_detections, 
                'total_detections': sum(len(v) for v in vulnerable_detections.values())
            },
            'anomaly_score': self.calculate_anomaly_score(secure_detections, vulnerable_detections)
        }
        
        return analysis
    
    def calculate_entropy(self, text):
        """Calcula entropía del texto"""
        if not text: return 0.0
        freq = {}
        for c in text[:4096]: 
            freq[c] = freq.get(c, 0) + 1
        total = len(text)
        e = 0.0
        for count in freq.values():
            p = count / total
            if p > 0: e -= p * math.log2(p)
        return min(e, self.max_entropy)
    
    def calculate_anomaly_score(self, secure_dets, vulnerable_dets):
        """Calcula score de anomalía entre nodos"""
        secure_total = sum(len(v) for v in secure_dets.values())
        vulnerable_total = sum(len(v) for v in vulnerable_dets.values())
        
        if secure_total == 0:
            return vulnerable_total * 10  # Máxima anomalía
        
        return (vulnerable_total - secure_total) / secure_total
    
    def save_training_data(self, analysis):
        """Guarda data de training para el modelo"""
        filename = f"/app/training_data/injection_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return filename
    
    def run_detection(self):
        """Loop principal de detección"""
        self.log.info("🕷️ Injection Detector Started - Training Mode")
        
        while True:
            try:
                # 1. Análisis comparativo
                analysis = self.compare_node_behaviors()
                
                # 2. Guardar training data
                training_file = self.save_training_data(analysis)
                
                # 3. Log de resultados
                anomaly = analysis['anomaly_score']
                secure_dets = analysis['secure_node']['total_detections']
                vuln_dets = analysis['vulnerable_node']['total_detections']
                
                if anomaly > 1.0:
                    self.log.warning(f"🚨 HIGH ANOMALY: {anomaly:.2f} | Secure: {secure_dets} | Vulnerable: {vuln_dets}")
                    self.log.info(f"💾 Training data: {training_file}")
                else:
                    self.log.info(f"✅ Normal: {anomaly:.2f} | S:{secure_dets} | V:{vuln_dets}")
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.log.error(f"🔧 Detection error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    detector = InjectionDetector()
    detector.run_detection()
