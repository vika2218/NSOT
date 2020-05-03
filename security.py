import sys
import datetime
import scapy
from scapy.all import *
from scapy.contrib.openflow import *
import subprocess as sub
import os
import re
import time
src_port = '46688'
src = '192.168.56.102'
import logging
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('log.txt')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

def detect():
        """
        Detection of DOS attach
        """
        s= sniff(filter="tcp and port 6653 and host 192.168.0.2", iface= "eth0", timeout=10)
        c=0
        print("----------")
        for i in s:
            try:
                if (i[3].type) ==10:
                    c+=1
                    if c == 100:
                        print("Attack detected!!!")
                        logger.warning("Attack detected!!!")
                        print("count------> {}".format(c))
                        return True
            except:
                pass
def stop():
        op= subprocess.check_output("sudo iptables -L INPUT", shell=True)
        op1= str(op).split("\\n")
        if op1.count("DROP       tcp  --  mininet.sns_bridge   anywhere             tcp spt:46688 dpt:6653") >=1:
            print("Rule already present")
            logger.info("Rule already present")
            return 0
        stop_att = ['sudo', 'iptables', '-A', 'INPUT', '-p', 'tcp', '-s', '192.168.0.2', '--dport', '6653', '--sport', src_port, '-j', 'DROP']
        check = ['sudo', 'iptables', '-L', '-n', '-v']
        sub.Popen(stop_att, stdout=sub.PIPE)
        print("Rule has been added in iptables")
        logger.info("Rule has been added")
while 1:
        sig= detect()
        if sig:
            stop()
        time.sleep(2)



