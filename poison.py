import os
import json
import random
import datetime
from scapy.all import IP, TCP
from netfilterqueue import NetfilterQueue

LOG_FILE = "/home/admin-sirpt/aegis_morph/mutation_logs.json"

def log_event(event_type, src_port, new_ttl):
    """
    Appends packet mutation data to the central intelligence feed.
    Synchronized with the JSON array structure used by the Dashboard.
    """
    new_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event_type,
        "ip": "LOCAL_OUTBOUND",
        "details": f"Port: {src_port} | Mutated TTL: {new_ttl}"
    }

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(new_entry)

    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def mutate_packet(packet):
    """
    Intercepts and modifies outgoing TCP/IP packets at Layer 3/4.
    Alters Time-To-Live (TTL) and TCP Window sizes to spoof OS fingerprints,
    creating a Moving Target Defense (MTD) effect against reconnaissance.
    """
    try:
        scapy_pkt = IP(packet.get_payload())

        if scapy_pkt.haslayer(TCP):
            # Define realistic OS profiles to confuse Nmap OS Detection
            # Windows: TTL 128 | Cisco IOS: TTL 255 | Linux: TTL 64 | Solaris: TTL 254
            os_profiles = [
                {"os": "Windows", "ttl": 128, "window": random.randint(8000, 8192)},
                {"os": "Cisco", "ttl": 255, "window": random.randint(4000, 4128)},
                {"os": "Linux", "ttl": 64,  "window": random.randint(5800, 5840)},
                {"os": "Solaris", "ttl": 254, "window": random.randint(8100, 8192)}
            ]

            # Select a random OS profile for this specific packet
            profile = random.choice(os_profiles)
            scapy_pkt.ttl = profile["ttl"]
            scapy_pkt[TCP].window = profile["window"]

            # Delete checksums to force Scapy to recalculate them accurately
            del scapy_pkt[IP].chksum
            del scapy_pkt[TCP].chksum

            # Inject the mutated packet back into the network stream
            packet.set_payload(bytes(scapy_pkt))

            print(f"[*] Polymorphic Shift: Spoofing {profile['os']} (TTL: {profile['ttl']}, Win: {profile['window']})")
            log_event("MTD_MUTATION", scapy_pkt[TCP].sport, profile['ttl'])

    except Exception as e:
        # Failsafe: Log the error but do not disrupt network flow
        pass

    finally:
        # Release the packet to continue its journey through the Linux kernel
        packet.accept()

if __name__ == "__main__":
    print("[*] Initializing Aegis Morph Polymorphic Engine (MTD)...")
    print("[*] Hooking into Netfilter Queue 1 for dynamic OS signature spoofing.")

    try:
        nfqueue = NetfilterQueue()
        # Bind to queue 1, matching the iptables NFQUEUE rule
        nfqueue.bind(1, mutate_packet)
        nfqueue.run()
    except KeyboardInterrupt:
        print("\n[*] Terminating Polymorphic Engine.")
    except Exception as e:
        print(f"[CRITICAL] Engine failure: {e}")
        print("[!] Ensure iptables rules are configured and running as root.")