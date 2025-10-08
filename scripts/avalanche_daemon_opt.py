# avalanche_daemon_opt.py - VERSIÓN CORREGIDA
#!/usr/bin/env python3
import time, logging, subprocess as sp, json, math

class AvalancheDaemon:
    def __init__(self):
        self.target = "avalanche_node_logger_service"  # ✅ Contenedor correcto
        self.interval = 30
        self.max_entropy = 3.14
        self._setup_log()
    
    def _setup_log(self):
        logging.basicConfig(filename='/app/daemon_logs/avalanche.log', level=logging.INFO, format='%(asctime)s | %(message)s')
        self.log = logging.getLogger()
    
    def _get_status(self):
        try:
            cmd = f"docker ps -f name={self.target} --format json"
            result = sp.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                return {'status': 'running', 'health': data.get('Health', '')}
            return {'status': 'not_found'}
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}
    
    def _get_logs(self):
        try:
            cmd = f"docker logs --tail 10 {self.target} 2>&1"
            result = sp.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except:
            return ""
    
    def _calc_entropy(self, text):
        if not text: return 0.0
        freq = {}
        for c in text[:2048]: freq[c] = freq.get(c, 0) + 1
        total = len(text)
        e = 0.0
        for count in freq.values():
            p = count / total
            if p > 0: e -= p * math.log2(p)
        return min(e, self.max_entropy)
    
    def _analyze(self, logs):
        err = logs.count('error') + logs.count('Error')
        warn = logs.count('warning') + logs.count('Warning')
        return err, warn
    
    def run(self):
        self.log.info("START")
        while True:
            try:
                status = self._get_status()
                logs = self._get_logs()
                entropy = self._calc_entropy(logs)
                err, warn = self._analyze(logs)
                
                if status['status'] == 'running':
                    if entropy < 2.5 and err == 0:
                        self.log.info(f"OK | E:{entropy:.2f}%")
                    elif entropy > 2.8 or err > 0:
                        self.log.warning(f"WARN | E:{entropy:.2f}% | ERR:{err}")
                    if entropy > 3.0:
                        self.log.error(f"HIGH_E | {entropy:.2f}%")
                else:
                    self.log.error("NOT_FOUND")
                
                time.sleep(self.interval)
            except Exception as e:
                self.log.error(f"LOOP_ERR: {e}")
                time.sleep(60)

if __name__ == "__main__":
    AvalancheDaemon().run()
