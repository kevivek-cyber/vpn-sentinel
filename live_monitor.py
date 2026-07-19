import time
import sys
import threading
import requests
from scapy.all import sniff, IP, TCP, UDP
API_URL = "http://127.0.0.1:8000/api/ingest"
FLUSH_INTERVAL = 3.0
FLOW_TIMEOUT = 10.0
active_flows = {}
lock = threading.Lock()
class FlowTracker:
    def __init__(self, src_ip, dst_ip, src_port, dst_port, proto):
        self.key = (src_ip, dst_ip, src_port, dst_port, proto)
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.first_time = time.time()
        self.last_time = time.time()
        self.fwd_lengths = []
        self.bwd_lengths = []
        self.timestamps = []
    def add_packet(self, pkt, direction):
        current_time = time.time()
        pkt_len = len(pkt)
        if direction == "fwd":
            self.fwd_lengths.append(pkt_len)
        else:
            self.bwd_lengths.append(pkt_len)
        self.timestamps.append(current_time)
        self.last_time = current_time
    def get_stats(self):
        duration = self.last_time - self.first_time
        if duration <= 0:
            duration = 0.01
        fwd_mean = sum(self.fwd_lengths) / len(self.fwd_lengths) if self.fwd_lengths else 0.0
        bwd_mean = sum(self.bwd_lengths) / len(self.bwd_lengths) if self.bwd_lengths else 0.0
        
        fwd_max = float(max(self.fwd_lengths)) if self.fwd_lengths else 0.0
        fwd_min = float(min(self.fwd_lengths)) if self.fwd_lengths else 0.0
        bwd_max = float(max(self.bwd_lengths)) if self.bwd_lengths else 0.0
        bwd_min = float(min(self.bwd_lengths)) if self.bwd_lengths else 0.0
        
        fwd_std = (sum((x - fwd_mean) ** 2 for x in self.fwd_lengths) / len(self.fwd_lengths)) ** 0.5 if len(self.fwd_lengths) > 1 else 0.0
        bwd_std = (sum((x - bwd_mean) ** 2 for x in self.bwd_lengths) / len(self.bwd_lengths)) ** 0.5 if len(self.bwd_lengths) > 1 else 0.0

        iats = []
        if len(self.timestamps) > 1:
            iats = [self.timestamps[i] - self.timestamps[i-1] for i in range(1, len(self.timestamps))]
        iat_mean = sum(iats) / len(iats) if iats else 0.1
        iat_std = (sum((x - iat_mean) ** 2 for x in iats) / len(iats)) ** 0.5 if len(iats) > 1 else 0.05
        
        iat_max = float(max(iats)) if iats else 0.1
        iat_min = float(min(iats)) if iats else 0.1

        total_packets = len(self.fwd_lengths) + len(self.bwd_lengths)
        packets_per_sec = total_packets / duration
        return {
            "duration": duration,
            "fwd_pkt_len_mean": max(40.0, fwd_mean),
            "bwd_pkt_len_mean": max(40.0, bwd_mean),
            "flow_iat_mean": max(0.001, iat_mean),
            "flow_iat_std": max(0.0005, iat_std),
            "packets_per_sec": max(1.0, packets_per_sec),
            "fwd_pkt_len_max": fwd_max,
            "fwd_pkt_len_min": fwd_min,
            "bwd_pkt_len_max": bwd_max,
            "bwd_pkt_len_min": bwd_min,
            "fwd_pkt_len_std": fwd_std,
            "bwd_pkt_len_std": bwd_std,
            "flow_iat_max": iat_max,
            "flow_iat_min": iat_min
        }
def packet_handler(pkt):
    if not pkt.haslayer(IP):
        return
    ip = pkt[IP]
    proto = ip.proto
    if pkt.haslayer(TCP):
        sport, dport = pkt[TCP].sport, pkt[TCP].dport
    elif pkt.haslayer(UDP):
        sport, dport = pkt[UDP].sport, pkt[UDP].dport
    else:
        return
    src_ip, dst_ip = ip.src, ip.dst
    print(".", end="", flush=True)
    fwd_key = (src_ip, dst_ip, sport, dport, proto)
    bwd_key = (dst_ip, src_ip, dport, sport, proto)
    with lock:
        if fwd_key in active_flows:
            active_flows[fwd_key].add_packet(pkt, "fwd")
        elif bwd_key in active_flows:
            active_flows[bwd_key].add_packet(pkt, "bwd")
        else:
            tracker = FlowTracker(src_ip, dst_ip, sport, dport, proto)
            tracker.add_packet(pkt, "fwd")
            active_flows[fwd_key] = tracker
def report_loop():
    """Periodically calculates statistics and pushes them to FastAPI backend"""
    while True:
        time.sleep(FLUSH_INTERVAL)
        now = time.time()
        to_report = []
        to_delete = []
        with lock:
            for key, flow in list(active_flows.items()):
                if len(flow.timestamps) >= 3:
                    to_report.append((flow.key, flow.get_stats()))
                if now - flow.last_time > FLOW_TIMEOUT:
                    to_delete.append(key)
            for key in to_delete:
                del active_flows[key]
        for key, stats in to_report:
            try:
                response = requests.post(API_URL, json=stats, timeout=2.0)
                if response.ok:
                    data = response.json()
                    status_str = f"VPN [{data['vpn_protocol']}]" if data['is_vpn'] else "Clean"
                    print(f"\n[Flow {key[0]}:{key[2]} -> {key[1]}:{key[3]}] Classed as: {status_str} (Conf: {data['confidence']*100:.1f}%)")
                    print(f"       Stats: Dur={stats['duration']:.1f}s | FwdLen={stats['fwd_pkt_len_mean']:.1f} | BwdLen={stats['bwd_pkt_len_mean']:.1f} | IAT={stats['flow_iat_mean']:.3f} | Pkts/s={stats['packets_per_sec']:.1f}")
                else:
                    print(f"\n[Backend Error] API returned status code {response.status_code}")
            except Exception as e:
                print(f"\n[Backend Connection Error] Could not connect to FastAPI server. Is it running on http://127.0.0.1:8000? Details: {e}")
if __name__ == "__main__":
    print("="*60)
    print("           VPN-Sentinel Live Traffic Sniffer")
    print("="*60)
    import socket
    from scapy.all import conf
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"
    active_iface = None
    for iface_name, iface in conf.ifaces.items():
        if getattr(iface, 'ip', None) == local_ip:
            active_iface = iface
            break
    if active_iface:
        print(f"Auto-detected active network interface: {active_iface.name} (IP: {local_ip})")
    else:
        print(f"Sniffing on default interface (Local IP: {local_ip})")
    print("Capturing live packets, extracting features, and pushing to local API...")
    thread = threading.Thread(target=report_loop, daemon=True)
    thread.start()
    try:
        if active_iface:
            sniff(iface=active_iface, prn=packet_handler, store=0, promisc=False)
        else:
            sniff(prn=packet_handler, store=0, promisc=False)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: On Windows, packet sniffing requires Npcap to be installed.")
        print("You can download it from: https://npcap.com/")
