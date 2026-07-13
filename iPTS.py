#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
iperf3 Performance Test Suite (iPTS) - v2.0
Author: SYLHETYHACKVENGER (THE-ERROR808)
For educational and authorised network testing only.
"""

import os
import sys
import subprocess
import time
import re
import itertools
from datetime import datetime

# ---------- ANSI Color Codes ----------
RESET = "\033[0m"
LIGHT_GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"
DRAGON_RED = "\033[91;1m"

# ---------- Banner (from https://www.asciiart.eu/art/c848c08b0a8e2a24) ----------
BANNER = r"""
                               ______________
                         ,===:'.,            `-._
                       `:.`---.__         `-._
                     `:.     `--.         `.
                   \.        `.         `.
            (,,(,    \.         `.   ____,-`.
         (,'     `/   \.   ,--.___`.
      ,  ,'  ,--.  `,   \.;'
       `{D, {    \  :    \;
         V,,'    /  /    //
         j;;    /  ,' ,-//.    ,---.      ,
         \;'   /  ,' /  _  \  /  _  \   ,'/
               \   `'  / \  `'  / \  `.' /
                `.___,'   `.__,'   `.__,'  VZ
"""

# ---------- Test Definitions ----------
# Each test: id, name, category, cmd_template, happens, cause, consequences

TESTS = [
    # ========== BANDWIDTH & THROUGHPUT (1-10) ==========
    {
        "id": 1,
        "name": "Measure TCP download throughput",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server}",
        "happens": "Client downloads data from server; measures throughput.",
        "cause": "TCP default mode; data flows from server to client.",
        "consequences": "Reveals download speed; identifies receive-side bottlenecks."
    },
    {
        "id": 2,
        "name": "Measure TCP upload throughput",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server} -R",
        "happens": "Server sends data to client; measures upload speed from client perspective.",
        "cause": "Reverse mode (-R) makes server the sender.",
        "consequences": "Reveals upload speed; identifies send-side bottlenecks."
    },
    {
        "id": 3,
        "name": "Measure UDP throughput",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server} -u -b {bandwidth}",
        "happens": "UDP packets sent at specified rate; server reports received bandwidth.",
        "cause": "UDP mode (-u) with bandwidth limit (-b).",
        "consequences": "Measures raw UDP throughput, loss, and jitter."
    },
    {
        "id": 4,
        "name": "Compare wired vs Wi‑Fi speed",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server}",
        "happens": "Run same command on wired and wireless interfaces separately.",
        "cause": "Comparison reveals performance differences.",
        "consequences": "Quantifies gap; helps decide which connection to use."
    },
    {
        "id": 5,
        "name": "Test LAN capacity",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server}",
        "happens": "Measures throughput between two hosts on same LAN.",
        "cause": "Local network constraints.",
        "consequences": "Identifies LAN max speed."
    },
    {
        "id": 6,
        "name": "Test WAN link capacity",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server}",
        "happens": "Measures throughput to a public server.",
        "cause": "ISP bandwidth and internet congestion.",
        "consequences": "Reveals actual WAN throughput."
    },
    {
        "id": 7,
        "name": "Test VPN bandwidth performance",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server}",
        "happens": "Throughput over VPN tunnel.",
        "cause": "VPN encryption and encapsulation add overhead.",
        "consequences": "Quantifies VPN performance impact."
    },
    {
        "id": 8,
        "name": "Test cloud server network speed",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server}",
        "happens": "Measures throughput to a cloud instance.",
        "cause": "Cloud provider network and location.",
        "consequences": "Helps choose optimal region."
    },
    {
        "id": 9,
        "name": "Test server NIC performance",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server} -P {parallel}",
        "happens": "Multi‑stream test stresses NIC.",
        "cause": "NIC offloading and driver efficiency.",
        "consequences": "Reveals NIC max throughput."
    },
    {
        "id": 10,
        "name": "Verify advertised network speeds",
        "category": "Bandwidth & Throughput",
        "cmd": "iperf3 -c {server} -b {bandwidth}",
        "happens": "Set target bandwidth to match advertised speed.",
        "cause": "Tests if ISP delivers promised speed.",
        "consequences": "Validates advertised speed."
    },

    # ========== TCP PERFORMANCE (11-20) ==========
    {
        "id": 11,
        "name": "Test TCP maximum throughput",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -P {parallel} -w {window}",
        "happens": "Multiple streams with large window push TCP to max.",
        "cause": "Parallel streams and window scaling.",
        "consequences": "Shows peak TCP capacity."
    },
    {
        "id": 12,
        "name": "Compare single TCP stream performance",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server}",
        "happens": "Single‑stream throughput.",
        "cause": "Single connection performance.",
        "consequences": "Baseline for multi‑stream comparison."
    },
    {
        "id": 13,
        "name": "Test multiple TCP streams",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -P {parallel}",
        "happens": "Aggregated throughput with multiple streams.",
        "cause": "Parallel connections fill the pipe.",
        "consequences": "Reveals total available bandwidth."
    },
    {
        "id": 14,
        "name": "Test TCP congestion behavior",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -C {congestion}",
        "happens": "Different CC algorithms affect throughput.",
        "cause": "Algorithms react differently to loss/latency.",
        "consequences": "Helps choose optimal CC."
    },
    {
        "id": 15,
        "name": "Test TCP window scaling",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -w {window}",
        "happens": "Window size affects throughput on long‑fat networks.",
        "cause": "Window determines in‑flight data.",
        "consequences": "Identifies optimal window size."
    },
    {
        "id": 16,
        "name": "Analyze TCP stability over time",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -t {duration} -i {interval}",
        "happens": "Long‑duration test shows fluctuations.",
        "cause": "Network conditions change over time.",
        "consequences": "Reveals stability and intermittent drops."
    },
    {
        "id": 17,
        "name": "Compare TCP performance between devices",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server}",
        "happens": "Run from Device A to B, then B to A.",
        "cause": "Hardware and OS differences.",
        "consequences": "Identifies which device performs better."
    },
    {
        "id": 18,
        "name": "Test high‑latency TCP connections",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -w {window}",
        "happens": "Large window compensates for high RTT.",
        "cause": "Bandwidth‑delay product requires large windows.",
        "consequences": "Tests if TCP can saturate long‑fat networks."
    },
    {
        "id": 19,
        "name": "Measure TCP retransmission impact",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} --verbose",
        "happens": "Verbose output shows retransmission counts.",
        "cause": "Packet loss triggers retransmissions.",
        "consequences": "Quantifies loss impact."
    },
    {
        "id": 20,
        "name": "Test different TCP durations",
        "category": "TCP Performance",
        "cmd": "iperf3 -c {server} -t {duration}",
        "happens": "Tests with varying test lengths.",
        "cause": "Steady state may take time.",
        "consequences": "Helps choose appropriate test duration."
    },

    # ========== UDP TESTING (21-30) ==========
    {
        "id": 21,
        "name": "Measure UDP bandwidth",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth}",
        "happens": "UDP packets sent at bitrate; server measures received.",
        "cause": "UDP mode with bandwidth limit.",
        "consequences": "Measures raw UDP throughput."
    },
    {
        "id": 22,
        "name": "Measure UDP packet loss",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth}",
        "happens": "Loss percentage is printed at end.",
        "cause": "Network drops packets due to congestion.",
        "consequences": "Identifies lossy links."
    },
    {
        "id": 23,
        "name": "Measure UDP jitter",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth}",
        "happens": "Jitter (delay variation) is printed.",
        "cause": "Queueing delays cause jitter.",
        "consequences": "High jitter degrades real‑time apps."
    },
    {
        "id": 24,
        "name": "Test real‑time traffic quality",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth} -l {length}",
        "happens": "Simulates real‑time traffic with small packets.",
        "cause": "UDP small packets at moderate rate.",
        "consequences": "Evaluates quality for VoIP/video."
    },
    {
        "id": 25,
        "name": "Simulate VoIP network conditions",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b 8M -l 200",
        "happens": "VoIP‑like traffic (64‑128 Kbps typically, but 8M is high for test).",
        "cause": "Small packets simulate voice.",
        "consequences": "Tests if network handles VoIP."
    },
    {
        "id": 26,
        "name": "Simulate video streaming requirements",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b 50M -l 1400",
        "happens": "Large packets at high rate simulate video.",
        "cause": "Video uses large frames.",
        "consequences": "Tests if network can sustain video bitrate."
    },
    {
        "id": 27,
        "name": "Test UDP packet size effects",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth} -l {length}",
        "happens": "Different packet sizes affect efficiency and loss.",
        "cause": "Packet size influences fragmentation.",
        "consequences": "Helps find optimal packet size."
    },
    {
        "id": 28,
        "name": "Check network reliability under UDP load",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b 1G -t {duration}",
        "happens": "High‑rate UDP flood tests network stability.",
        "cause": "Extreme UDP load may cause buffer drops.",
        "consequences": "Reveals network resilience."
    },
    {
        "id": 29,
        "name": "Compare UDP vs TCP performance",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth}",
        "happens": "Run TCP and UDP tests separately.",
        "cause": "Different protocol characteristics.",
        "consequences": "Helps choose protocol for application."
    },
    {
        "id": 30,
        "name": "Analyze UDP behavior across routers",
        "category": "UDP Testing",
        "cmd": "iperf3 -c {server} -u -b {bandwidth}",
        "happens": "Run with different router paths.",
        "cause": "Router queueing policies affect UDP.",
        "consequences": "Identifies router behaviour."
    },

    # ========== LATENCY & STABILITY (31-40) ==========
    {
        "id": 31,
        "name": "Observe throughput variation",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -i 0.5",
        "happens": "Throughput reported every 0.5 seconds.",
        "cause": "Time‑series analysis.",
        "consequences": "Detects bursty performance."
    },
    {
        "id": 32,
        "name": "Measure network consistency",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -i 1 -t 300",
        "happens": "Long test with 1‑second intervals.",
        "cause": "Stability over time.",
        "consequences": "Confirms network reliability."
    },
    {
        "id": 33,
        "name": "Find unstable links",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -i 0.5 -t 60",
        "happens": "Short test with fine granularity.",
        "cause": "Sudden drops indicate instability.",
        "consequences": "Pinpoints problematic links."
    },
    {
        "id": 34,
        "name": "Detect intermittent problems",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -i 0.2 -t 120",
        "happens": "Very fine interval captures brief drops.",
        "cause": "External interference or throttling.",
        "consequences": "Reveals issues short tests miss."
    },
    {
        "id": 35,
        "name": "Monitor long‑running connections",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -t 7200 -i 60",
        "happens": "2‑hour test with 1‑minute reporting.",
        "cause": "Long‑term degradation.",
        "consequences": "Helps identify memory leaks or overheating."
    },
    {
        "id": 36,
        "name": "Compare latency conditions",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server}",
        "happens": "Run at different times of day.",
        "cause": "Network load varies.",
        "consequences": "Identifies best and worst times."
    },
    {
        "id": 37,
        "name": "Identify congestion periods",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server}",
        "happens": "Run at peak (8 PM) and off‑peak (3 AM).",
        "cause": "Congestion during busy hours.",
        "consequences": "Helps plan usage or upgrades."
    },
    {
        "id": 38,
        "name": "Test peak‑hour performance",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -P 16",
        "happens": "Heavy load during peak hours.",
        "cause": "High concurrency.",
        "consequences": "Reveals worst‑case performance."
    },
    {
        "id": 39,
        "name": "Verify network upgrades",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server}",
        "happens": "Run before and after upgrade.",
        "cause": "Compare performance delta.",
        "consequences": "Validates upgrade effectiveness."
    },
    {
        "id": 40,
        "name": "Track performance changes over time",
        "category": "Latency & Stability",
        "cmd": "iperf3 -c {server} -J >> history.json",
        "happens": "Periodic JSON logging.",
        "cause": "Trend analysis.",
        "consequences": "Enables proactive maintenance."
    },

    # ========== WI‑FI TESTING (41-50) ==========
    {
        "id": 41,
        "name": "Compare 2.4 GHz vs 5 GHz Wi‑Fi",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server}",
        "happens": "Connect to each band and run test.",
        "cause": "Band differences.",
        "consequences": "Helps choose best band."
    },
    {
        "id": 42,
        "name": "Test Wi‑Fi access point capacity",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server} -P 10",
        "happens": "Multiple streams stress the AP.",
        "cause": "AP CPU and backhaul.",
        "consequences": "Reveals AP capacity."
    },
    {
        "id": 43,
        "name": "Test Wi‑Fi roaming performance",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server} -t 300 -i 1",
        "happens": "Walk while running; observe drops.",
        "cause": "Handoff latency.",
        "consequences": "Evaluates roaming quality."
    },
    {
        "id": 44,
        "name": "Measure wireless throughput",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server}",
        "happens": "Basic Wi‑Fi throughput test.",
        "cause": "Wireless overhead.",
        "consequences": "Quantifies real‑world Wi‑Fi speed."
    },
    {
        "id": 45,
        "name": "Find weak Wi‑Fi areas",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server}",
        "happens": "Run from different locations.",
        "cause": "Signal strength variations.",
        "consequences": "Maps coverage."
    },
    {
        "id": 46,
        "name": "Test Wi‑Fi under multiple streams",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server} -P 4",
        "happens": "Multiple streams saturate Wi‑Fi.",
        "cause": "Contention.",
        "consequences": "Reveals total capacity."
    },
    {
        "id": 47,
        "name": "Compare different Wi‑Fi adapters",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server}",
        "happens": "Test each adapter.",
        "cause": "Hardware differences.",
        "consequences": "Helps choose best adapter."
    },
    {
        "id": 48,
        "name": "Test router wireless capability",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server} -P 8 -t 60",
        "happens": "Stresses router's Wi‑Fi.",
        "cause": "Router CPU and chipset.",
        "consequences": "Determines if router is limiting."
    },
    {
        "id": 49,
        "name": "Check wireless stability",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server} -t 600 -i 10",
        "happens": "Long test checks for fluctuations.",
        "cause": "Interference or overheating.",
        "consequences": "Identifies unstable Wi‑Fi."
    },
    {
        "id": 50,
        "name": "Evaluate home Wi‑Fi quality",
        "category": "Wi‑Fi Testing",
        "cmd": "iperf3 -c {server}",
        "happens": "Comprehensive single test.",
        "cause": "Overall network assessment.",
        "consequences": "Helps decide if upgrade needed."
    },

    # ========== SERVER & INFRASTRUCTURE (51-60) ==========
    {
        "id": 51,
        "name": "Test server network interfaces",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server} -P 8",
        "happens": "Multi‑stream tests NIC.",
        "cause": "Driver and hardware.",
        "consequences": "Verifies NIC performance."
    },
    {
        "id": 52,
        "name": "Benchmark server connections",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server}",
        "happens": "Basic server throughput.",
        "cause": "Server CPU and stack.",
        "consequences": "Helps size server."
    },
    {
        "id": 53,
        "name": "Test data center links",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server}",
        "happens": "Throughput inside DC.",
        "cause": "Switch fabric and cabling.",
        "consequences": "Validates DC network."
    },
    {
        "id": 54,
        "name": "Compare servers in different locations",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server}",
        "happens": "Run to multiple servers.",
        "cause": "Geographic distance and routing.",
        "consequences": "Helps choose optimal location."
    },
    {
        "id": 55,
        "name": "Test load balancer paths",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server}",
        "happens": "Test via load balancer VIP.",
        "cause": "LB algorithm and health.",
        "consequences": "Verifies LB performance."
    },
    {
        "id": 56,
        "name": "Verify network configuration changes",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server}",
        "happens": "Run before and after changes.",
        "cause": "Configuration affects throughput.",
        "consequences": "Confirms changes didn't degrade."
    },
    {
        "id": 57,
        "name": "Test firewall performance impact",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server} -p {port}",
        "happens": "Compare with and without firewall.",
        "cause": "Inspection overhead.",
        "consequences": "Quantifies firewall impact."
    },
    {
        "id": 58,
        "name": "Test router throughput",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server} -P 8",
        "happens": "Stress router forwarding.",
        "cause": "Router CPU and memory.",
        "consequences": "Identifies router bottleneck."
    },
    {
        "id": 59,
        "name": "Test switch performance",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server}",
        "happens": "Test within same subnet.",
        "cause": "Switch fabric.",
        "consequences": "Validates switch performance."
    },
    {
        "id": 60,
        "name": "Validate network upgrades",
        "category": "Server & Infrastructure",
        "cmd": "iperf3 -c {server} -P 8 -t 60",
        "happens": "Pre‑ and post‑upgrade comparison.",
        "cause": "Upgraded hardware/bandwidth.",
        "consequences": "Confirms upgrade success."
    },

    # ========== ADVANCED CONFIGURATION (61-71) ==========
    {
        "id": 61,
        "name": "Test custom ports",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -p {port}",
        "happens": "Traffic on non‑default port.",
        "cause": "Firewall rules may restrict.",
        "consequences": "Tests port‑based filtering."
    },
    {
        "id": 62,
        "name": "Test IPv4 performance",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -4",
        "happens": "Force IPv4.",
        "cause": "IPv4 stack.",
        "consequences": "IPv4 baseline."
    },
    {
        "id": 63,
        "name": "Test IPv6 performance",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -6",
        "happens": "Force IPv6.",
        "cause": "IPv6 stack.",
        "consequences": "Compares IPv4 vs IPv6."
    },
    {
        "id": 64,
        "name": "Bind tests to specific interfaces",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -B {interface}",
        "happens": "Traffic forced through specific source IP.",
        "cause": "Multi‑homed host.",
        "consequences": "Tests interface‑specific performance."
    },
    {
        "id": 65,
        "name": "Run parallel streams",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -P {parallel}",
        "happens": "Multiple concurrent streams.",
        "cause": "Parallelism increases utilisation.",
        "consequences": "Reveals total bandwidth."
    },
    {
        "id": 66,
        "name": "Run reverse direction tests",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -R",
        "happens": "Server sends, client receives.",
        "cause": "Reverse mode.",
        "consequences": "Tests download direction."
    },
    {
        "id": 67,
        "name": "Run bidirectional tests",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} --bidir",
        "happens": "Simultaneous upload and download.",
        "cause": "Bidirectional mode.",
        "consequences": "Simulates real‑world traffic."
    },
    {
        "id": 68,
        "name": "Export results in JSON format",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -J",
        "happens": "Output in JSON.",
        "cause": "Machine‑readable.",
        "consequences": "Enables automation and graphing."
    },
    {
        "id": 69,
        "name": "Automate tests with scripts",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -t 10 -J > result.json",
        "happens": "Run from bash/Python script.",
        "cause": "Automation.",
        "consequences": "Enables scheduled tests."
    },
    {
        "id": 70,
        "name": "Schedule regular performance checks",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -J >> /var/log/iperf.log",
        "happens": "Cron job runs regularly.",
        "cause": "Continuous monitoring.",
        "consequences": "Provides performance history."
    },
    {
        "id": 71,
        "name": "Build monitoring dashboards",
        "category": "Advanced Configuration",
        "cmd": "iperf3 -c {server} -J",
        "happens": "Send JSON to Prometheus/Grafana.",
        "cause": "Integration with monitoring tools.",
        "consequences": "Real‑time visibility."
    }
]

# Group mapping for menu
GROUPS = {
    1: {"name": "Bandwidth & Throughput", "start": 1, "end": 10},
    2: {"name": "TCP Performance", "start": 11, "end": 20},
    3: {"name": "UDP Testing", "start": 21, "end": 30},
    4: {"name": "Latency & Stability", "start": 31, "end": 40},
    5: {"name": "Wi‑Fi Testing", "start": 41, "end": 50},
    6: {"name": "Server & Infrastructure", "start": 51, "end": 60},
    7: {"name": "Advanced Configuration", "start": 61, "end": 71},
}

# ---------- Helper Functions ----------
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    for line in BANNER.split('\n'):
        if line.strip():
            print(f"{DRAGON_RED}{line}{RESET}")
        else:
            print(line)

def print_header():
    print(f"{LIGHT_GREEN}{'='*60}{RESET}")
    print(f"{CYAN}>> IPERF3 TEST SUITE v2.0 (71 TESTS) <<{RESET}")
    print(f"{DIM}Author: SYLHETYHACKVENGER (THE-ERROR808){RESET}")
    print(f"{DIM}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{LIGHT_GREEN}{'='*60}{RESET}")
    print(f"{YELLOW}⚠️  ALL TESTS RUN WITH SUDO ⚠️{RESET}")
    print(f"{LIGHT_GREEN}{'='*60}{RESET}")
    print()

def show_loading(message="Loading test details", duration=1):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{CYAN}{next(spinner)} {message}...{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"\r{LIGHT_GREEN}✓ {message} complete.   {RESET}\n")
    sys.stdout.flush()

def show_countdown(seconds=3):
    print(f"{YELLOW}🚀 Starting test in:{RESET}")
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{CYAN}⏳ {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write(f"\r{LIGHT_GREEN}⚡ GO! ⚡{RESET}\n\n")
    sys.stdout.flush()

def show_main_menu():
    print(f"\n{LIGHT_GREEN}--- MAIN MENU ---{RESET}")
    for key, val in GROUPS.items():
        print(f"{BOLD}{key}{RESET}. {val['name']} (tests {val['start']}-{val['end']})")
    print(f"{BOLD}10{RESET}. Show ALL tests (choose any to execute)")
    print(f"{BOLD}11{RESET}. Help (iperf3 -h)")
    print(f"{BOLD}0{RESET}. Exit")
    choice = input(f"{CYAN}[?] Enter choice: {RESET}").strip()
    return choice

def show_tests_in_group(group_id):
    group = GROUPS.get(group_id)
    if not group:
        return None
    start, end = group['start'], group['end']
    print(f"\n{LIGHT_GREEN}--- {group['name']} TESTS ---{RESET}")
    for i in range(start, end+1):
        test = TESTS[i-1]
        print(f"{BOLD}{i}{RESET}. {test['name']}")
    print(f"{BOLD}0{RESET}. Back to main menu")
    choice = input(f"{CYAN}[?] Select test number (or 0): {RESET}").strip()
    if choice.isdigit():
        return int(choice)
    return None

def display_all_tests():
    print(f"\n{LIGHT_GREEN}{'='*60}{RESET}")
    print(f"{CYAN}ALL {len(TESTS)} TESTS (select any by number){RESET}")
    print(f"{LIGHT_GREEN}{'-'*60}{RESET}")
    for i, test in enumerate(TESTS, start=1):
        print(f"{BOLD}{i:3d}{RESET}. {test['name']} [{test['category']}]")
    print(f"{LIGHT_GREEN}{'='*60}{RESET}")
    while True:
        sel = input(f"{CYAN}[?] Enter test number to execute (0 to cancel): {RESET}").strip()
        if sel == '0':
            return None
        if sel.isdigit() and 1 <= int(sel) <= len(TESTS):
            return int(sel)
        print(f"{RED}[!] Invalid input. Enter a number between 1 and {len(TESTS)}, or 0 to cancel.{RESET}")

def display_test_info(test):
    print(f"\n{LIGHT_GREEN}{'='*60}{RESET}")
    print(f"{CYAN}TEST #{test['id']}: {test['name']}{RESET}")
    print(f"{LIGHT_GREEN}{'-'*60}{RESET}")
    print(f"{BOLD}Category:{RESET} {test['category']}")
    print(f"{BOLD}Command:{RESET} {test['cmd']}")
    print(f"{LIGHT_GREEN}{'-'*60}{RESET}")
    print(f"{BOLD}🔍 What happens:{RESET} {test['happens']}")
    print(f"{BOLD}⚙️  Cause:{RESET} {test['cause']}")
    print(f"{BOLD}💥 Consequences:{RESET} {test['consequences']}")
    print(f"{LIGHT_GREEN}{'='*60}{RESET}")

def get_placeholders(cmd_template):
    placeholders = {}
    found = set(re.findall(r'\{([^}]+)\}', cmd_template))
    for ph in found:
        if ph == 'server':
            val = input(f"{CYAN}[?] Enter server IP/hostname (required): {RESET}").strip()
            while not val:
                print(f"{RED}[!] Server IP is required.{RESET}")
                val = input(f"{CYAN}[?] Enter server IP/hostname: {RESET}").strip()
        elif ph == 'port':
            val = input(f"{CYAN}[?] Enter port (press Enter to skip, iperf3 default 5201): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'duration':
            val = input(f"{CYAN}[?] Enter duration in seconds (press Enter for default, usually 10): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'bandwidth':
            val = input(f"{CYAN}[?] Enter bandwidth (e.g., 100M, press Enter for default, usually unlimited): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'parallel':
            val = input(f"{CYAN}[?] Enter number of parallel streams (press Enter for default, usually 1): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'window':
            val = input(f"{CYAN}[?] Enter TCP window size (e.g., 256K, press Enter to skip): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'length':
            val = input(f"{CYAN}[?] Enter packet length in bytes (press Enter to skip): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'interval':
            val = input(f"{CYAN}[?] Enter reporting interval in seconds (press Enter to skip): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'congestion':
            val = input(f"{CYAN}[?] Enter congestion control algorithm (cubic, bbr, reno) (press Enter to skip): {RESET}").strip()
            if val == '':
                val = None
        elif ph == 'interface':
            val = input(f"{CYAN}[?] Enter source IP to bind (e.g., 192.168.1.100) (press Enter to skip): {RESET}").strip()
            if val == '':
                val = None
        else:
            val = input(f"{CYAN}[?] Enter value for {ph} (press Enter to skip): {RESET}").strip()
            if val == '':
                val = None
        placeholders[ph] = val
    return placeholders

def build_command(cmd_template, placeholders):
    cmd = cmd_template
    for ph, val in placeholders.items():
        if val is None:
            # Remove the flag and the placeholder from the command.
            import re
            pattern = r'\s*\-{1,2}[a-zA-Z]+\s+\{' + re.escape(ph) + r'\}\s*'
            cmd = re.sub(pattern, ' ', cmd)
            cmd = re.sub(r'\s*\{' + re.escape(ph) + r'\}\s*', ' ', cmd)
        else:
            cmd = cmd.replace('{' + ph + '}', val)
    # Clean up extra spaces
    cmd = ' '.join(cmd.split())
    return cmd

def execute_test(test_id):
    if test_id < 1 or test_id > len(TESTS):
        print(f"{RED}[!] Invalid test ID.{RESET}")
        return
    test = TESTS[test_id-1]

    show_loading("Loading test details", 1)
    display_test_info(test)

    placeholders = get_placeholders(test['cmd'])
    final_cmd = build_command(test['cmd'], placeholders)

    if not final_cmd.strip() or final_cmd == "iperf3":
        print(f"{RED}[!] Command is empty. Please provide required server.{RESET}")
        return

    final_cmd = "sudo " + final_cmd

    show_countdown(3)

    print(f"\n{LIGHT_GREEN}>>> LIVE OUTPUT ({datetime.now().strftime('%H:%M:%S')}) <<<{RESET}")
    print(f"{DIM}Command: {final_cmd}{RESET}")
    print(f"{LIGHT_GREEN}{'-'*60}{RESET}")

    proc = subprocess.Popen(final_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in proc.stdout:
        print(f"{LIGHT_GREEN}{line}{RESET}", end='')
    proc.wait()
    print(f"{LIGHT_GREEN}{'-'*60}{RESET}")
    print(f"{CYAN}=== TEST FINISHED (exit code {proc.returncode}) ==={RESET}")
    if proc.returncode != 0:
        print(f"{YELLOW}[!] Command exited with code {proc.returncode}{RESET}")

def show_help():
    print(f"{CYAN}[*] Displaying iperf3 help...{RESET}")
    subprocess.run(["iperf3", "-h"])

def main():
    clear_screen()
    print_banner()
    print_header()

    while True:
        choice = show_main_menu()
        if choice == '0':
            print(f"{CYAN}[*] Exiting...{RESET}")
            break
        elif choice == '10':
            sel = display_all_tests()
            if sel is not None:
                execute_test(sel)
                input(f"{DIM}Press Enter to continue...{RESET}")
                clear_screen()
                print_banner()
                print_header()
        elif choice == '11':
            show_help()
            input(f"{DIM}Press Enter to continue...{RESET}")
            clear_screen()
            print_banner()
            print_header()
        elif choice.isdigit() and int(choice) in GROUPS:
            group_id = int(choice)
            while True:
                sel = show_tests_in_group(group_id)
                if sel == 0:
                    break
                if sel is not None and 1 <= sel <= len(TESTS):
                    execute_test(sel)
                    input(f"{DIM}Press Enter to continue...{RESET}")
                    clear_screen()
                    print_banner()
                    print_header()
                else:
                    print(f"{RED}[!] Invalid selection.{RESET}")
        else:
            print(f"{RED}[!] Invalid choice.{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrupted by user.{RESET}")
        sys.exit(0)
