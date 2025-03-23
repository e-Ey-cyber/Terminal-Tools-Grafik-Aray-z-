import psutil
import threading
import time

class ResourceManager:
    def __init__(self):
        self.monitoring = False
        self._lock = threading.Lock()
        self.thresholds = {
            'cpu': 90,    # %90 CPU kullanımı
            'memory': 85, # %85 RAM kullanımı
            'disk': 95    # %95 Disk kullanımı
        }
        
    def start_monitoring(self):
        """Start resource monitoring"""
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._monitor_resources, daemon=True).start()

    def _monitor_resources(self):
        """Monitor system resources"""
        while self.monitoring:
            with self._lock:
                usage = {
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent
                }
                
                # Check thresholds
                for resource, value in usage.items():
                    if value > self.thresholds[resource]:
                        print(f"⚠️ {resource.upper()} usage critical: {value}%")
            
            time.sleep(5)  # Check every 5 seconds
