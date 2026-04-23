import asyncio

async def handle_attacker(reader, writer):
    # Get attacker IP for the Attacker Profile Card
    addr = writer.get_extra_info('peername')
    print(f"[🚨] GHOST SHIP ALERT: Scanner detected from IP {addr[0]} on fake port {addr[1]}")
    
    # Try to capture their reconnaissance payload to feed the AI
    try:
        data = await asyncio.wait_for(reader.read(1024), timeout=2.0)
        if data:
            print(f"    [📦] Payload captured: {data.hex()}")
    except asyncio.TimeoutError:
        pass

    # Abruptly drop the connection to confuse their tools
    writer.close()
    await writer.wait_closed()

async def deploy_phantom_network(start_port, end_port):
    servers = []
    print(f"[*] Initializing Aegis Morph Deception Layer...")
    
    for port in range(start_port, end_port + 1):
        try:
            server = await asyncio.start_server(handle_attacker, '0.0.0.0', port)
            servers.append(server)
        except Exception:
            continue # Skip if port is legitimately in use
    
    print(f"[✅] Ghost Ship deployed! Listening on {len(servers)} fake ports.")
    await asyncio.gather(*[s.serve_forever() for s in servers])

if __name__ == "__main__":
    # Test range: Deploying 100 fake ports
    asyncio.run(deploy_phantom_network(1000, 1100))
