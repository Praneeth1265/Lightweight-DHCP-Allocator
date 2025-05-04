import socket
import uuid
import platform
import subprocess
import os
import time

def get_mac():
    mac = hex(uuid.getnode()).replace('0x', '').upper()     #GETS THE MAC ADDRESS
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))

def set_ip(ip, subnet, gateway, dns):
    os_type = platform.system()                             #GETS THE TYPE OF OS (WINDIWS,DARWIN,LINUX)
    print(f"[SETUP] Configuring IP {ip} on {os_type}")
    
    if os_type == "Windows":
        subprocess.call(f'netsh interface ip set address name="Wi-Fi" static {ip} {subnet} {gateway}', shell=True)    #DIRECTLY TO RUN IN THE TERMINAL TO CHANGE IP ADDRESS
        subprocess.call(f'netsh interface ip set dns name="Wi-Fi" static {dns}', shell=True)
    elif os_type == "Darwin":
        os.system(f"sudo ifconfig en0 inet {ip} netmask {subnet} alias")
    elif os_type == "Linux":
        os.system(f"sudo ifconfig wlan0 {ip} netmask {subnet}")
        os.system(f"sudo route add default gw {gateway}")
        with open("/etc/resolv.conf", "w") as f:
            f.write(f"nameserver {dns}\n")
    else:
        print("[!] Unsupported OS")

def release_ip(ip):                         #DIRECTLY TO REMOVE THE IP ASSIGNED BY THE DHCP SERVER
    os_type = platform.system()
    print(f"[RELEASE] Releasing IP on {os_type}")

    if os_type == "Windows":
        subprocess.call('netsh interface ip set address name="Wi-Fi" dhcp', shell=True)
    elif os_type == "Darwin":
        os.system(f"sudo ifconfig en0 -alias {ip}")
    elif os_type == "Linux":
        os.system(f"sudo ip addr del {ip}/24 dev wlan0")
    else:
        print("[!] Unsupported OS")

def main():
    mac = get_mac().replace(":", "")
    print(f"[INFO] MAC Address: {mac}")         

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)         #UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(10)

    server_port = 6767                  
    broadcast_address = ('<broadcast>', server_port)           

    try:
        print("[DISCOVER] Broadcasting to find DHCP server...")
        sock.sendto(f"DISCOVER:{mac}".encode(), broadcast_address)

        data, server_addr = sock.recvfrom(1024)
        message = data.decode()

        if message.startswith("OFFER:"):
            parts = message.split(":")
            offered_ip = parts[1]
            subnet = parts[2]
            gateway = parts[3]
            dns = parts[4]
            first_hop = parts[5] if len(parts) > 5 else gateway 
            print(f"[OFFER] IP: {offered_ip}, Subnet: {subnet}, Gateway: {gateway}, DNS: {dns}, FirstHop: {first_hop}")

            # Send REQUEST
            sock.sendto(f"REQUEST:{mac}:{offered_ip}".encode(), server_addr)
            data, _ = sock.recvfrom(1024)
            ack = data.decode()

            if ack.startswith("ACK:"):
                print(f"[ACK] IP {offered_ip} assigned successfully!")
                set_ip(offered_ip, subnet, gateway, dns)
                print("[TIMER] IP will be released in 20 seconds...")
                time.sleep(20)
                release_ip(offered_ip)
                print("[RELEASED] IP released.")
            else:
                print("[NAK] Server denied IP request.")

        else:
            print("[!] Unexpected response from server.")

    except socket.timeout:
        print("[TIMEOUT] No response from server.")
    finally:
        sock.close()
        print("[DISCONNECTED] UDP socket closed.")

if __name__ == "__main__":
    main()