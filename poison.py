from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP
import random
import json
import time
import os

# Absolute path to ensure the file is created in your project folder
LOG_FILE = "/home/admin-sirpt/aegis_morph/mutation_logs.json"

def mutate(packet):
    pkt = IP(packet.get_payload())
    if pkt.haslayer(TCP):
        # 🎭 MTD Mutation Logic
        fake_ttl = random.choice([128, 255])
        pkt.ttl = fake_ttl
        pkt[TCP].window = random.randint(1000, 5000)
        
        del pkt[IP].chksum
        del pkt[TCP].chksum
        
        packet.set_payload(bytes(pkt))
        
        # Data for your Pôle 2 deliverable
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "MTD_MUTATION",
            "src_port": pkt[TCP].sport,
            "new_ttl": fake_ttl
        }
        
        # Append to log file
        try:
            with open(LOG_FILE, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Logging Error: {e}")
            
        print(f"[🧬] AEGIS MORPH: Mutated TTL to {fake_ttl}")
    
    packet.accept()

print(f"[*] Aegis Morph Engine Active. Logging to: {LOG_FILE}")
nfqueue = NetfilterQueue()
nfqueue.bind(1, mutate)
nfqueue.run()
