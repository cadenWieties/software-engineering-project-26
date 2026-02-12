# udp_comm.py
import socket
import threading
from typing import Callable
from config import AppConfig

class UDPComm:
    
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        
        # Sender socket
        self.tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tx.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Receiver socket: bind to any interface so it can receive from any IP
        self.rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rx.bind(("0.0.0.0", cfg.udp_receive_port))
        
        self._stop = threading.Event()
        self._thread = None
    
    @property
    def target_ip(self) -> str:
        # Returns target IP
        return self.cfg.udp_target_ip
    
    def set_target_ip(self, ip: str) -> None:
        # Change network address used for UDP sends
        self.cfg.udp_target_ip = ip
        
    
    def send_equipment_id(self, equipment_id: int) -> None:
        # Broadcast equipment id after player addition
        # Transmission format is a single integer
        payload = str(equipment_id).encode("utf-8")
        self.tx.sendto(payload, (self.cfg.udp_target_ip, self.cfg.udp_send_port))
        
    def start_receiver(self, on_message: Callable[[str, tuple], None]) -> None:
        # Tests by calling on_message(payload_str, addr)
        if self._thread and self._thread.is_alive():
            return
        
        self._stop.clear()
        
        def loop():
            while not self._stop.is_set():
                try:
                    data, addr = self.rx.recvfrom(2048)
                    msg = data.decode("utf-8", errors="replace").strip()
                    on_message(msg, addr)
                except OSError:
                    break
        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
    
    def close(self):
        self._stop.set()
        try:
            self.rx.close()
        finally:
            self.tx.close()
            