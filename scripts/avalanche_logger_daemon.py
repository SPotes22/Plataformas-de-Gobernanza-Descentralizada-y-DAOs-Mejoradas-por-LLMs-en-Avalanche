#!/usr/bin/env python3
"""
AvalancheNodeLoggerDaemon - Entropía 2.89%
Monitorea específicamente: avalanche_node_logger_service
Complejidad ciclo-somática: 3
"""
import time
import logging
import subprocess
import json
import math
from pathlib import Path
import re

class AvalancheLoggerDaemon:
    def __init__(self):
        self.target_container = "avalanche_node_logger_service"
        self.check_interval = 30
        self.max_entropy = 3.14
        self.setup_logging()
    
    def setup_logging(self):
        """Configuración de logging - Complejidad: 2"""
        logging.basicConfig(
            filename='avalanche_daemon.log',
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger()
    
    def get_container_status(self):
        """Obtiene estado del contenedor - Complejidad: 2"""
        try:
            cmd = f"docker ps --filter name={self.target_container} --format json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                container_data = json.loads(result.stdout)
                return {
                    'status': 'running',
                    'name': container_data.get('Names', ''),
                    'state': container_data.get('State', ''),
                    'health': container_data.get('Health', '')
                }
            return {'status': 'not_found'}
            
        except Exception as e:
            self.logger.error(f"Error checking container: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def calculate_log_entropy(self, log_chunk):
        """Calcula entropía de logs - Complejidad: 3"""
        if not log_chunk:
            return 0.0
        
        char_freq = {}
        total_chars = len(log_chunk)
        
        for char in log_chunk[:4096]:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        entropy = 0.0
        for count in char_freq.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return min(entropy, self.max_entropy)
    
    def get_container_logs(self, lines=50):
        """Obtiene logs del contenedor - Complejidad: 2"""
        try:
            cmd = f"docker logs --tail {lines} {self.target_container} 2>&1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except Exception as e:
            self.logger.error(f"Log retrieval failed: {e}")
            return ""
    
    def analyze_log_patterns(self, logs):
        """Analiza patrones en logs - Complejidad: 3"""
        patterns = {
            'error': len(re.findall(r'error|Error|ERROR', logs)),
            'warning': len(re.findall(r'warning|Warning|WARNING', logs)),
            'block': len(re.findall(r'block|Block', logs)),
            'transaction': len(re.findall(r'transaction|Transaction', logs))
        }
        return patterns
    
    def monitor_avalanche_node(self):
        """Monitoreo principal - Complejidad: 3"""
        self.logger.info(f"🕷️ Starting monitoring for: {self.target_container}")
        
        while True:
            try:
                # 1. Verificar estado del contenedor
                status = self.get_container_status()
                
                # 2. Obtener y analizar logs
                logs = self.get_container_logs(20)
                entropy = self.calculate_log_entropy(logs)
                patterns = self.analyze_log_patterns(logs)
                
                # 3. Log de estado según condición
                if status['status'] == 'running':
                    health_status = status.get('health', 'unknown')
                    
                    # Estado normal
                    if entropy < 2.0 and patterns['error'] == 0:
                        self.logger.info(
                            f"✅ {self.target_container} | "
                            f"Health: {health_status} | "
                            f"Entropy: {entropy:.2f}% | "
                            f"Blocks: {patterns['block']}"
                        )
                    
                    # Estado con advertencia
                    elif entropy > 2.5 or patterns['error'] > 0:
                        self.logger.warning(
                            f"🚨 {self.target_container} | "
                            f"Entropy: {entropy:.2f}% | "
                            f"Errors: {patterns['error']} | "
                            f"Warnings: {patterns['warning']}"
                        )
                    
                    # Estado crítico
                    if entropy > 3.0:
                        self.logger.error(
                            f"🔴 CRITICAL ENTROPY: {entropy:.2f}% | "
                            f"Container: {self.target_container}"
                        )
                        
                elif status['status'] == 'not_found':
                    self.logger.error(f"❌ Container not found: {self.target_container}")
                    
                else:
                    self.logger.error(f"⚠️ Container status error: {status}")
                
                # 4. Esperar hasta siguiente verificación
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Daemon stopped by user")
                break
                
            except Exception as e:
                self.logger.error(f"🔧 Monitoring loop error: {e}")
                time.sleep(60)

def main():
    """Función principal - Complejidad: 1"""
    daemon = AvalancheLoggerDaemon()
    daemon.monitor_avalanche_node()

if __name__ == "__main__":
    main()
