import psutil
import os
import subprocess
import platform
import distro

class SystemMonitor:
    @staticmethod
    def get_cpu_usage():
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_memory_usage():
        return psutil.virtual_memory().percent

    @staticmethod
    def get_disk_usage():
        return psutil.disk_usage('/').percent

    @staticmethod
    def get_network_stats():
        return psutil.net_io_counters()

    @staticmethod
    def get_running_processes():
        return len(psutil.pids())

    @staticmethod
    def check_root():
        return os.geteuid() == 0

    @staticmethod
    def get_system_info():
        """Sistem bilgilerini getir"""
        return {
            'os': distro.name(True),
            'kernel': platform.release(),
            'arch': platform.machine(),
            'cpu': platform.processor(),
            'ram_total': psutil.virtual_memory().total,
            'swap_total': psutil.swap_memory().total,
            'python_version': platform.python_version()
        }

    @staticmethod
    def get_disk_partitions():
        """Disk bölümlerini listele"""
        return [partition._asdict() for partition in psutil.disk_partitions()]

    @staticmethod
    def get_services_status():
        """Servis durumlarını kontrol et"""
        services = ['NetworkManager', 'ssh', 'cups', 'apache2', 'mysql']
        status = {}
        for service in services:
            try:
                subprocess.check_call(['systemctl', 'is-active', service],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                status[service] = 'active'
            except subprocess.CalledProcessError:
                status[service] = 'inactive'
        return status

    @staticmethod
    def get_boot_time():
        """Sistem başlangıç zamanını getir"""
        return psutil.boot_time()

    @staticmethod
    def get_resource_usage():
        """Detaylı kaynak kullanımı"""
        return {
            'cpu_freq': psutil.cpu_freq(),
            'cpu_stats': psutil.cpu_stats(),
            'memory': psutil.virtual_memory()._asdict(),
            'swap': psutil.swap_memory()._asdict(),
            'disk_io': psutil.disk_io_counters(),
            'network_io': psutil.net_io_counters()
        }

    def get_system_info(self):
        """Get formatted system info with emojis"""
        return {
            '💻 İşletim Sistemi': distro.name(True),
            '🔄 Kernel': platform.release(),
            '⚙️ Mimari': platform.machine(),
            '🔲 CPU': platform.processor(),
            '📊 RAM': self.format_bytes(psutil.virtual_memory().total),
            '💾 Swap': self.format_bytes(psutil.swap_memory().total)
        }

    @staticmethod
    def format_bytes(bytes):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
