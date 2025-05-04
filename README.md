# Lightweight-DHCP-Allocator
A Python-based DHCP server-client system using raw UDP sockets. Implements DORA protocol (Discover, Offer, Request, Acknowledge) for dynamic IP assignment in LANs. Features OS-aware config, multithreading, auto subnet/gateway/DNS detection.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Features
  
  **DORA Protocol Implementation**:  
  - **Discover**: Client broadcasts a `DHCPDISCOVER` message to locate servers.  
  - **Offer**: Server responds with a `DHCPOFFER` containing an available IP.  
  - **Request**: Client formally requests the offered IP via `DHCPREQUEST`.  
  - **Acknowledge**: Server confirms with `DHCPACK`, finalizing the lease.
- DHCPOFFER includes DNS Server, First-Hop Router's IP, Default Gateway
- Real-time IP allocation via **UDP sockets** (ports 67/68).  
- OS-aware automatic configuration (Windows/Linux/macOS support).  
- Multithreaded server logic for concurrent client handling.  
- Auto-detection of subnet, gateway, and DNS settings.
- A pool of allocated IP's corresponding to the user's MAC address which ensures unambiguity.

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Use Cases  

- Local network testing and debugging.  
- Educational projects on DHCP protocols.  
- Temporary IP assignment in lab environments. 
