import asyncio
import json
import datetime
import os

def log_event(event_type, attacker_ip, details=""):
    """
    Appends threat intelligence data to the central JSON log.
    Acts as the telemetry feed for the Aegis Command Center.
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

async def handle_attacker(reader, writer):
    """
    Routes the adversary to a specific high-interaction deception module.
    Personality routing is determined mathematically to ensure consistency.
    """
    addr = writer.get_extra_info('peername')
    sock = writer.get_extra_info('sockname')
    attacker_ip = addr[0]
    port = sock[1]

    # Mathematical routing expanded to 5 distinct profiles
    personality_seed = port % 5

    print(f"[ALERT] Scanner detected from IP {attacker_ip} on port {port} (Profile {personality_seed})")
    log_event("GHOST_SHIP_DETECTION", attacker_ip, f"Targeting Profile {personality_seed} on port {port}")

    try:
        if personality_seed == 0:
            # Profile 0: Simulated Data Leak (Environmental Variables)
            fake_env = (
                "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n"
                "# DEBUG MODE ENABLED\nDB_HOST=127.0.0.1\nDB_USER=root\n"
                "DB_PASS=AegisSecret2026!\nAPI_KEY=sk_live_51MzXjHG92kd...\n"
            )
            writer.write(fake_env.encode())
            await writer.drain()
            await asyncio.sleep(10)

        elif personality_seed == 1:
            # Profile 1: Interactive Shell Mimicry
            writer.write(b"ubuntu@sirpt-victim:~$ ")
            await writer.drain()

            while True:
                data = await asyncio.wait_for(reader.read(1024), timeout=30.0)
                if not data:
                    break

                command = data.decode('utf-8', errors='ignore').strip()

                # Simulate processing latency before denying permission
                await asyncio.sleep(2.5)
                writer.write(f"sh: 1: {command}: Permission denied\nubuntu@sirpt-victim:~$ ".encode())
                await writer.drain()

                log_event("SHELL_MIMICRY", attacker_ip, f"Command attempted: {command}")

        elif personality_seed == 2:
            # Profile 2: Credential Harvesting Module
            writer.write(b"220-Development Backup Server\r\nLogin: ")
            await writer.drain()

            creds = await asyncio.wait_for(reader.read(1024), timeout=10.0)
            if creds:
                writer.write(b"331 Password required\r\nPassword: ")
                await writer.drain()

                passwd = await asyncio.wait_for(reader.read(1024), timeout=10.0)

                decoded_user = creds.decode('utf-8', errors='ignore').strip()
                decoded_pass = passwd.decode('utf-8', errors='ignore').strip()
                log_event("CREDENTIAL_HARVEST", attacker_ip, f"Captured: {decoded_user} / {decoded_pass}")

        elif personality_seed == 3:
            # Profile 3: Standard SSH Decoy with Latency
            writer.write(b"SSH-2.0-OpenSSH_8.2p1\r\n")
            await writer.drain()
            await asyncio.sleep(15)

        elif personality_seed == 4:
            # Profile 4: Active Defense Tool-Breaker (Infinite Payload)
            # Feeds an endless stream of JSON to exhaust the adversary's RAM and parsing tools.
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            await writer.drain()
            log_event("TOOL_SABOTAGE", attacker_ip, "Deploying infinite recursion payload")

            while True:
                # Transmit continuous data chunks
                writer.write(b'{"aegis_morph_data_leak":' * 50)
                await writer.drain()
                # 0.5s sleep prevents pegging our own server's CPU while holding the connection open
                await asyncio.sleep(0.5)

    except asyncio.TimeoutError:
        pass
    except Exception:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def deploy_phantom_network(start_port, end_port):
    """
    Initializes the asynchronous listeners to create the deception surface.
    """
    servers = []
    print("[*] Initializing Aegis Morph Deception Layer...")

    for port in range(start_port, end_port + 1):
        try:
            server = await asyncio.start_server(handle_attacker, '0.0.0.0', port)
            servers.append(server)
        except Exception:
            continue # Bypass ports currently utilized by the OS

    print(f"[+] Ghost Ship active. Listening on {len(servers)} high-interaction polymorphic ports.")
    await asyncio.gather(*[s.serve_forever() for s in servers])

if __name__ == "__main__":
    # Define the deception surface range
    asyncio.run(deploy_phantom_network(1000, 1100))
