import socket
import threading
import subprocess

# DHCP Server Configuration
ip_pool = [f"192.168.1.{i}" for i in range(150, 200)]  # Available IP pool
leased_ips = {}  # MAC to IP mapping
SERVER_IP = "0.0.0.0"
SERVER_PORT = 6767

# Windows-compatible network info fetching

def get_default_gateway():
    try:
        output = subprocess.check_output("ipconfig", shell=True, encoding='utf-8', errors='ignore')
        for line in output.splitlines():
            if "Default Gateway" in line:
                parts = line.split(":")
                if len(parts) >= 2 and parts[1].strip():
                    return parts[1].strip()
        return ""
    except Exception:
        return ""


def get_dns_server():
    try:
        output = subprocess.check_output("ipconfig /all", shell=True, encoding='utf-8', errors='ignore')
        for line in output.splitlines():
            if "DNS Servers" in line:
                parts = line.split(":")
                if len(parts) >= 2 and parts[1].strip():
                    return parts[1].strip()
        return ""
    except Exception:
        return ""


def get_subnet_mask():
    try:
        output = subprocess.check_output("ipconfig", shell=True, encoding='utf-8', errors='ignore')
        for line in output.splitlines():
            if "Subnet Mask" in line:
                parts = line.split(":")
                if len(parts) >= 2 and parts[1].strip():
                    return parts[1].strip()
        return ""
    except Exception:
        return ""


def handle_request(message, client_addr, sock):
    print(f"[DEBUG] Received from {client_addr}: {message}")
    parts = message.split(":")
    if len(parts) < 2:
        print(f"[WARN] Malformed message: {message}")
        return
    msg_type, mac = parts[0], parts[1]

    # Fetch network info once per request
    gateway = get_default_gateway() or "0.0.0.0"
    dns = get_dns_server() or ""
    subnet = get_subnet_mask() or "255.255.255.0"
    first_hop = gateway
    
    if msg_type == "DISCOVER":
        # Determine which IP to offer
        if mac in leased_ips:
            offered_ip = leased_ips[mac]
        elif ip_pool:
            offered_ip = ip_pool[0]
        else:
            offered_ip = None

        if not offered_ip:
            response = "NO_IP_AVAILABLE"
        else:
            response = f"OFFER:{offered_ip}:{subnet}:{gateway}:{dns}:{first_hop}"
            print(f"DNS: {dns}")
            print(f"Gateway: {gateway}")
            print(f"Subnet: {subnet}")
            print(f"First-hop addr: {first_hop}")
        sock.sendto(response.encode(), client_addr)
        print(f"[SEND] to {client_addr}: {response}")

    elif msg_type == "REQUEST":
        if len(parts) < 3:
            print(f"[WARN] REQUEST missing IP: {message}")
            return
        requested_ip = parts[2]
        # ACK only if matches an active offer or available in pool
        if mac in leased_ips and leased_ips[mac] == requested_ip:
            ack_ip = requested_ip
        elif requested_ip in ip_pool:
            ip_pool.remove(requested_ip)
            leased_ips[mac] = requested_ip
            ack_ip = requested_ip
        else:
            sock.sendto(b"NAK", client_addr)
            print(f"[NAK] to {client_addr}: {requested_ip}")
            return

        response = f"ACK:{ack_ip}:{subnet}:{gateway}:{dns}:{first_hop}"
        sock.sendto(response.encode(), client_addr)
        print(f"[SEND] to {client_addr}: {response}")

    else:
        print(f"[WARN] Unknown message type: {msg_type}")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((SERVER_IP, SERVER_PORT))

    print(f"[+] DHCP Server listening on UDP {SERVER_IP}:{SERVER_PORT}")
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8', errors='ignore')
            threading.Thread(target=handle_request, args=(message, addr, sock), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
