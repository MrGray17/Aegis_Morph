from scapy.all import sniff, IP, TCP, send
import json
import datetime
import os
import random

def log_event(event_type, attacker_ip, details=""):
    """
    Appends Layer 4 entrapment telemetry to the central intelligence feed.
    Synchronized with the JSON array structure utilized by the Dashboard.
    """
    log_file = 'mutation_logs.json'
    new_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event_type,
        "ip": attacker_ip,
        "details": details
    }

    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(new_entry)

    with open(log_file, 'w') as f:
        json.dump(data, f, indent=4)

def process_packet(pkt):
    """
    Intercepts TCP probes and crafts a deceptive, weaponized SYN-ACK response.
    Implements 'Window Jitter' to induce a Persist Timer state, alongside
    TCP Option Sabotage (MSS constraint) to cripple adversary stack buffers.
    Neutralizes SYN, FIN, NULL, and XMAS scanning techniques.
    """
    if pkt.haslayer(TCP):
        attacker_ip = pkt[IP].src
        target_port = pkt[TCP].dport
        tcp_flags = pkt[TCP].flags

        # Detect Standard (SYN) and Stealth (FIN, NULL, XMAS) scans
        if tcp_flags == "S" or tcp_flags == "F" or tcp_flags == "FPU" or tcp_flags == "":

            # Adaptive Persistence Logic (Window Jitter)
            fake_window = 0 if random.random() > 0.15 else random.choice([5, 10])

            # Supreme Protocol Sabotage: TCP Options
            # Forcing the attacker to use tiny Maximum Segment Sizes (MSS)
            # and disabling Window Scaling (WScale=0), breaking their throughput.
            sabotage_options = [('MSS', random.choice([48, 128, 256])), ('WScale', 0)]

            ip_layer = IP(dst=attacker_ip, src=pkt[IP].dst)

            # Dynamic Sequence Generation & Flag Manipulation
            # Always responding with SYN-ACK heavily confuses Nmap Stealth Scans
            tcp_layer = TCP(
                sport=target_port,
                dport=pkt[TCP].sport,
                flags="SA",
                seq=random.getrandbits(32),
                ack=pkt[TCP].seq + 1 if tcp_flags == "S" else 0,
                window=fake_window,
                options=sabotage_options
            )

            send(ip_layer/tcp_layer, verbose=False)

            # Telemetry Reporting
            scan_type = "SYN" if tcp_flags == "S" else "STEALTH"
            status = f"FROZEN (Win=0, MSS={sabotage_options[0][1]})" if fake_window == 0 else f"THROTTLED (Win={fake_window})"

            print(f"[ACTION] {scan_type} Scan Entrapped: {attacker_ip} -> {status} on port {target_port}")
            log_event("TARPIT_ENTRAPMENT", attacker_ip, f"Type: {scan_type} | State: {status} | Port: {target_port}")

if __name__ == "__main__":
    print("[*] Initializing Aegis Morph Supreme Protocol Tarpit...")
    print("[*] Active Modules: Window Jitter | TCP Option Sabotage | Multi-Vector Defense")

    # Sniff specifically for incoming TCP traffic to neutralize
    try:
        sniff(filter="tcp", prn=process_packet)
    except KeyboardInterrupt:
        print("\n[*] Terminating Protocol Tarpit.")
    except Exception as e:
        print(f"[CRITICAL] Tarpit failure: {e}")