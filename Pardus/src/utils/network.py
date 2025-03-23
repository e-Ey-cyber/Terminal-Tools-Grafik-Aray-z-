import socket
import requests
import subprocess
import netifaces
import speedtest

class NetworkUtils:
    @staticmethod
    def check_connection():
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False

    @staticmethod
    def get_ip_address():
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return None

    @staticmethod
    def ping(host):
        try:
            subprocess.run(["ping", "-c", "1", host], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
            return True
        except:
            return False

    @staticmethod
    def get_all_interfaces():
        """Tüm ağ arayüzlerini listele"""
        return netifaces.interfaces()

    @staticmethod
    def get_interface_info(interface):
        """Ağ arayüzü bilgilerini getir"""
        try:
            addrs = netifaces.ifaddresses(interface)
            return {
                'ipv4': addrs.get(netifaces.AF_INET, []),
                'ipv6': addrs.get(netifaces.AF_INET6, []),
                'mac': addrs.get(netifaces.AF_LINK, [])[0].get('addr')
            }
        except Exception:
            return None

    @staticmethod
    def speed_test():
        """İnternet hız testi yap"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            return {
                'download': st.download() / 1_000_000,  # Mbps
                'upload': st.upload() / 1_000_000,      # Mbps
                'ping': st.results.ping
            }
        except Exception:
            return None

    @staticmethod
    def traceroute(host):
        """Traceroute yap"""
        try:
            output = subprocess.check_output(['traceroute', host])
            return output.decode()
        except Exception:
            return None
