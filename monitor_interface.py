import time
import json
import os
import subprocess
import signal
import sys
from datetime import datetime, timedelta
from collections import Counter

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
BAN_THRESHOLD = 10
LOG_FILE = '/home/admin-sirpt/aegis_morph/mutation_logs.json'
INTERFACE = "ens33"
banned_ips = set()

def graceful_shutdown(sig, frame):
    """Intercepts Ctrl+C for a clean terminal exit."""
    print("\n\n[*] Terminating Aegis Morph Command Center...")
    print("[*] Flushing active session memory. Kernel blackholes remain active.")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)

def execute_countermeasure(ip):
    """
    Deploys targeted, autonomous countermeasures.
    Utilizes Kernel Route Blackholing for zero-CPU packet dropping,
    followed by a UFW rule for persistent Layer 3 isolation.
    """
    if ip in ["127.0.0.1", "0.0.0.0", "localhost"]:
        return

    print(f"\n[CRITICAL] THREAT THRESHOLD EXCEEDED FOR IP: {ip}")
    print("[*] Deploying Supreme Countermeasure: Kernel-Level Blackhole...")

    # 1. Route Blackholing: Drops packets at the routing layer (ISP level defense)
    subprocess.run(
        ["sudo", "ip", "route", "add", "blackhole", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # 2. UFW Deny: Ensures persistence and blocks incoming connections silently
    subprocess.run(
        ["sudo", "ufw", "insert", "1", "deny", "from", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    banned_ips.add(ip)
    print(f"[+] Target Neutralized: {ip} successfully blackholed.")

def calculate_threat_level(logs):
    """
    Calculates operational threat level based on event velocity.
    """
    if not logs:
        return "LOW (Nominal)"

    try:
        # Check events in the last 60 seconds
        now = datetime.now()
        recent_events = 0
        for entry in reversed(logs):
            log_time = datetime.strptime(entry.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
            if (now - log_time).total_seconds() < 60:
                recent_events += 1
            else:
                break

        if recent_events > 50:
            return "CRITICAL (Active Assault)"
        elif recent_events > 10:
            return "ELEVATED (Scanning Detected)"
        else:
            return "LOW (Nominal)"
    except Exception:
        return "CALCULATING..."

def display_dashboard():
    """
    Main loop for the Threat Intelligence Dashboard.
    Renders telemetry data, heuristics, and triggers automated response protocols.
    """
    while True:
        os.system('clear')
        print("=" * 85)
        print(" AEGIS MORPH | AUTONOMOUS THREAT INTELLIGENCE COMMAND CENTER (SIRPT)")
        print("=" * 85)
        print(f" [SYSTEM] NODE: ENSA-01 | INTERFACE: {INTERFACE} | TIME: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 85)

        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r') as f:
                    logs = json.load(f)

                # Telemetry Aggregation
                ghost_hits = sum(1 for entry in logs if "GHOST" in entry.get('event', ''))
                tarpit_hits = sum(1 for entry in logs if "TARPIT" in entry.get('event', ''))
                shell_hits = sum(1 for entry in logs if "SHELL" in entry.get('event', ''))
                cred_hits = sum(1 for entry in logs if "CREDENTIAL" in entry.get('event', ''))
                mtd_hits = sum(1 for entry in logs if "MTD" in entry.get('event', ''))
                tool_hits = sum(1 for entry in logs if "TOOL_SABOTAGE" in entry.get('event', ''))

                threat_level = calculate_threat_level(logs)

                print(f" [DEFCON] THREAT LEVEL: {threat_level}")
                print(f" [METRICS] TOTAL EVENTS: {len(logs)} | DECOY HITS: {ghost_hits} | TARPIT CATCHES: {tarpit_hits}")
                print(f" [INTELLIGENCE] SHELL: {shell_hits} | CREDENTIALS: {cred_hits} | TOOL SABOTAGE: {tool_hits}")
                print(f" [POLYMORPHISM] MTD PACKET MUTATIONS: {mtd_hits}")
                print("-" * 85)

                # Threat Analysis Engine
                ip_list = [entry.get('ip') for entry in logs if entry.get('ip') and entry.get('ip') != "LOCAL_OUTBOUND"]
                ip_counts = Counter(ip_list)

                for ip, count in ip_counts.items():
                    if count >= BAN_THRESHOLD and ip not in banned_ips:
                        execute_countermeasure(ip)

                print(" [ACTIVITY LOG] RECENT TELEMETRY:")
                for entry in logs[-8:]:
                    timestamp = entry.get('timestamp', 'N/A')
                    event = entry.get('event', 'UNKNOWN')
                    ip = entry.get('ip', 'Unknown')

                    marker = "[*]"
                    if "TARPIT" in event: marker = "[+]"
                    elif "CREDENTIAL" in event or "SHELL" in event or "SABOTAGE" in event: marker = "[!]"
                    elif "MTD" in event: marker = "[~]"

                    print(f"   {marker} [{timestamp}] {event:<22} | SRC: {ip}")

            except (json.JSONDecodeError, ValueError):
                print(" [WAITING] Initializing telemetry stream...")
        else:
            print(" [WAITING] Log file absent. Awaiting first intrusion event...")

        print("-" * 85)

        if banned_ips:
            print(f" [ISOLATED IPs (BLACKHOLED)]: {', '.join(banned_ips)}")

        print(" [DEFENSES] Active: Decoy Surface | Protocol Tarpit | MTD Polymorphism | Auto-Isolation")
        print(" Press Ctrl+C to terminate the Command Center.")

        time.sleep(1.5)

if __name__ == "__main__":
    display_dashboard()
