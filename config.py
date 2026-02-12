# config.py
from dataclasses import dataclass

@dataclass
class AppConfig:
    # Database config 
    db_host : str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "photon"
    db_user: str = "student"
    db_password: str = "student"
    
    # UDP config
    
    # Can change this in UI for Sprint 2
    udp_target_ip: str = "127.0.0.1"
    
    # Broadcast/Send here
    udp_send_port: int = 7500
    
    # Bind + Receive here
    udp_receive_port: int = 7501