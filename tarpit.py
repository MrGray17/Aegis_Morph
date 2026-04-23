from scapy.all import *

# This function targets the attacker's tool integrity and time [Aegis Morph Strategy]
def process_packet(pkt):
    if pkt.haslayer(TCP) and pkt[TCP].flags == "S": # Catching the SYN (First move)
        # Build the Mirage Response
        ip = IP(dst=pkt[IP].src, src=pkt[IP].dst)
        
        # The Secret Sauce: window=0
        # This forces the attacker's TCP stack into a 'Persist Timer' state
        tcp = TCP(sport=pkt[TCP].dport, dport=pkt[TCP].sport, 
                  flags="SA", seq=12345, ack=pkt[TCP].seq + 1, window=0)
        
        send(ip/tcp, verbose=False)
        print(f"[⏳] TARPIT: Attacker {pkt[IP].src} just got frozen on port {pkt[TCP].dport}")

print("[*] Aegis Morph Tarpit Active... Paralyzing automated tools.")
# Listening specifically on the ports we want to protect/trap
sniff(filter="tcp", prn=process_packet)
