import json
import re
import subprocess
import os
import csv
import ipaddress
from netmiko import ConnectHandler
import json
import time
from multiprocessing import Process
import requests


#csvfile = open('nsot_tn.csv', 'r')
#fieldnames = ("Hostname","Management IP","Username","Password","Router ID","Process", "Networks")
#global j
#j = csv.DictReader( csvfile, fieldnames)



def sdn_intent():
    with open('nsot_flowentries.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #print(row)
            if row['Protocol'] == "tcp":
                protocol = "6"
            elif row['Protocol'] == "udp":
                protocol = "17"
            controller_ip = row['Controller IP']
            dpid = row['DPID']
            priority = row['Priority']
            in_port = row['In Port']
            nw_src = row['Source IP']
            nw_dst = row['Destination IP']
            dl_type = row['Ethernet Type']
            nw_proto = row['Protocol']
            action = row['Action']
            tp_dst_port = row['Destination Port']
            push_flow_entry(controller_ip, protocol, dpid, priority, in_port, nw_src, nw_dst, dl_type, nw_proto, tp_dst_port, action)
    return 0

def push_flow_entry(controller_ip,protocol,dpid,priority,in_port,nw_src,nw_dst,dl_type,nw_proto,tp_dst_port,action):

    flow_entry_payload = {
        "dpid":   dpid ,
        "cookie":  priority ,
        "cookie_mask": 1,
        "table_id": 0,
        "idle_timeout": 3600,
        "hard_timeout": 3600,
        "priority":  priority ,
        "flags": 1,
        "match":{
            "in_port":  in_port ,
            "nw_src":  nw_src ,
            "nw_dst": nw_dst ,
            "dl_type":  dl_type ,
            "nw_proto": protocol,
            "tp_dst_port":  tp_dst_port
        },
        "actions":[
            {
                "type":"OUTPUT",
                "port": action
            }
        ]
        }

    r = requests.post("http://{}:8080/stats/flowentry/add" .format(controller_ip),json= flow_entry_payload )
    return 0


def read_csv():
    csvfile = open('nsot_tn.csv', 'r')
    fieldnames = ("Hostname","Management IP","Username","Password","Router ID","Process", "Networks")
    reader = csv.DictReader( csvfile, fieldnames)
    return(reader)


def exception_handling():
    j= read_csv()

    for i in j:
        #print(i["Management IP"])
        try:
            (ipaddress.IPv4Address(i["Management IP"]))
        except:
            print("\nWrong Management IP address: {}. Exiting the code ...".format(i["Management IP"]))
            quit()
    return 0

def get_wmask(ip):
    interface = ipaddress.IPv4Interface(ip)
    subnet = str(interface.netmask)
    wildcard = []
    for x in subnet.split('.'):
        component = 255 - int(x)
        wildcard.append(str(component))
    wildcard = '.'.join(wildcard)

    return(str(interface.ip), str(wildcard))

def ospf_func(**i):
        cisco = {
            'device_type': 'cisco_ios',
            'host': i['Management IP'],
            'username': i['Username'],
            'password': i['Password'],
        }

        cmds=[]
        cmds.append( "router ospf {} \nrouter-id {}".format(i['Process'],i['Router ID'] ))
        for k in i['Networks'].split(' '):
            cmds.append("\nnetwork {} {} area {}".format(get_wmask(k.split(",")[0])[0],get_wmask(k.split(",")[0])[1], k.split(",")[1]))

        print(cmds)
        netconnect = ConnectHandler(**cisco)
        op=netconnect.send_config_set(cmds, cmd_verify=False)
        print("op--->", op)
        netconnect.disconnect()
        print("-----")
        return 0


def hostname(**i):
        cisco = {
            'device_type': 'cisco_ios',
            'host': i['Management IP'],
            'username': i['Username'],
            'password': i['Password'],
        }
        cmds=[]
        cmds.append("hostname {}".format(i['Hostname'] ))
        #print(cmds)
        netconnect=ConnectHandler(**cisco)
        op=netconnect.send_config_set(cmds)
        #print("op---->",op)
        cmds="sh run | sec hostname"
        op= netconnect.send_command(cmds)
        print("Hostname configured  on=", op.split(" ")[1])
        netconnect.disconnect()
        print("-----")
        return (op.split(" ")[1])


def sh_down_int(**i):
    downInt={}

    
    cisco = {
        'device_type': 'cisco_ios',
        'host': i['Management IP'],
        'username': i['Username'],
        'password': i['Password'],
        }
    #cmds=[]
    #cmds.append("hostname {}".format(i['Hostname'] ))
    cmd="sh ip int b"
    #print(cmds)
    netconnect=ConnectHandler(**cisco)
    op= netconnect.send_command(cmd)
    downIntList=[]
    hname=str(i["Hostname"])
    #print("Down Interfaces for router {}\n".format(i['Hostname']))
    op1= (op.split("\n")[1:])
    for i in op1:
        i1= (str(i).split(" "))
        if i1.count('up') !=2:
            #print("Down-->{}".format(i1[0]))
            downIntList.append(i[0:16]+ i[50:])
           # downIntList.append("</br></br>")
            
    downInt[hname]=downIntList
    print("-----")
    output=(json.dumps(downInt, indent=5))
    f= open("shut_tmp.txt","a")
    f.write(output+"</br></br>")
    f.close()
    #return (json.dumps(downInt, indent=5))


def sdn_disconnected_sw():
    nsot = {}
    c = {'device_type': 'linux', 'username': 'sns', 'password': 'sns', 'ip': '192.168.0.2'}

#    conn = ConnectHandler(**c)
    #print("Connected")
#    output = conn.send_command('sudo ovs-vsctl show')
    output= subprocess.check_output("ssh sns@192.168.0.2 sudo ovs-vsctl show", shell=True)
    #output = conn.send_command_timing('sns')
    #print("output----->",output )
    output = str(output).rstrip()
    op = output.split("Bridge")
    for i in range(1, len(op)):
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', op[i])
        port = re.findall(r'66[5|3]3', op[i])
        opt = op[i].rstrip('\n')
        p = opt.split()
        p1 = p[0].replace("\"", "")[0:2]
        nsot[p1] = {}
        nsot[p1]['Controller IP'] = ip[0]
        nsot[p1]['Openflow Port'] = port[0]
      #  output = conn.send_command_timing('sudo ovs-ofctl show ' + p1)
        if 'is_connected:' in op[i]:
            nsot[p1]['Connected'] = 'True'
        else:
            nsot[p1]['Connected'] = 'False'
        if "WARN" in output:
            nsot[p1]['OF_Version'] = 'OpenFlow13'
        else:
            nsot[p1]['OF_Version'] = 'OpenFlow10'
    disconnected_list=[]
    for i in nsot.keys():
        if nsot[i]['Connected'] == 'False':
            disconnected_list.append(i.rstrip())
    print("Disconnected switches--->",disconnected_list)
    return("Disconnected switches--->" + str(disconnected_list))
    #conn.disconnect()
def security():
    subprocess.call("ssh sns@192.168.0.3 sudo python3 security.py &", shell=True)
    print("Security module started on SDN Controller")
    return 0
def helper_ospf():
    j = read_csv()
    process_list=[]
    for i in j:
        p = Process(target= ospf_func, kwargs= i)
        p.start()
        process_list.append(p)
    for i in process_list:
        i.join()


def helper_hostname():
    j = read_csv()
    process_list=[]
    for i in j:
        p = Process(target= hostname, kwargs= i)
        p.start()
        process_list.append(p)
#    for i in process_list:
#        i.join()

def helper_shut():
    j = read_csv()
    with open("shut_tmp.txt","w") as f:
        f.write("Down interfaces: </br>")
        pass
    process_list=[]
    for i in j:
        p = Process(target= sh_down_int, kwargs= i)
        p.start()
        process_list.append(p)
    for i in process_list:
        i.join()
    with open("shut_tmp.txt","r") as f:
    #f= open("shut_tmp.txt", "r")
        #print(f.read())
        a = f.read()
    os.remove("shut_tmp.txt")
    print("Down Interfaces: \n", a)
    return (str(a))

def helper_pushfe():
    p = Process(target= sdn_intent)
    p.start()

def helper_github():
    cmds=["git add .", "git commit -m .", "git push origin master"]
    for i in cmds:
        try:
                op= subprocess.check_output(i, shell=True)
                print(op)

        except:
                pass
    print("\nNSOT pushed successfully to GitHub")


def helper_security():
    p = Process(target=security)
    p.start()
exception_handling()
#sh_down_int()
##jsonfile.write(out)
#exception_handling(j)
#ospf_func(j)
#helper_hostname(j)
#helper_ospf(j)
#sh_disconnected_switches()
#helper_shut(j)
#hostname(j)
#csvfile.close()
#sdn_intent()
#sdn_disconnected_sw()
