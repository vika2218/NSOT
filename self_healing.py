from netmiko import ConnectHandler
import csv
import re
import subprocess
import ipaddress
from multiprocessing import Process
import os
import datetime


# Function to Read CSV File
def read_csv():
    csvfile = open('nsot_tn.csv', 'r')
    fieldnames = ("Hostname","Management IP","Username","Password","Router ID","Process", "Networks")
    reader = csv.DictReader( csvfile, fieldnames)
    return(reader)


# Function to Get Wildcard_mask
def get_wmask(ip):
    interface = ipaddress.IPv4Interface(ip)
    subnet = str(interface.netmask)
    wildcard = []
    for x in subnet.split('.'):
        component = 255 - int(x)
        wildcard.append(str(component))
    wildcard = '.'.join(wildcard)
    return(str(interface.ip), str(wildcard))


#Function to Detect OSPF Issues
def ospf_detect():
    log = open("foo.txt", "a")
    j = read_csv()
    expectedNN = {}
    actualN= {}
    list_faulty_router = []
    for r in j:
        expectedNN[r['Hostname']] = len(r['Networks'].split(' '))
        cisco = {
            'device_type': 'cisco_ios',
            'host': r['Management IP'],
            'username': r['Username'],
            'password': r['Password'],
            }
        net_connect=ConnectHandler(**cisco)
        a = net_connect.send_command('show ip ospf neighbor')        
        a = a.split('\n')
        try:
            a.remove('')
        except:
            pass
        if len(a) == 1:
            print("No Neighbors for " + r['Hostname'])
            log.write("No Neighbors for " + r['Hostname'] + " <br/>")
            actualN[r['Hostname']] = 0
            list_faulty_router.append(r['Hostname'])
        else:
            print("Number of neighbors for " + r['Hostname'] + " is " + str(len(a) - 1))
            log.write("\nNumber of neighbors for " + r['Hostname'] + " is " + str(len(a) - 1) + " <br/>")
            actualN[r['Hostname']] = len(a) - 1
            if expectedNN[r['Hostname']] != int(len(a) - 1):
                list_faulty_router.append(r['Hostname'])
    print("Misconfigured Routers: ",list_faulty_router)
    if list_faulty_router == []:
        print("No errors detected in OSPF for any router")
    ospf_healing(list_faulty_router)
    log.write("\n List of routers having OSPF misconfiguration: " + str(list_faulty_router) + " <br/>")
    log.close()
    return(list_faulty_router)


# Function to Solve Issues in OSPF
def ospf_healing(L):
    log = open("foo.txt", "a")
    j = read_csv()
    for i in j:
        cisco = {
            'device_type': 'cisco_ios',
            'host': i['Management IP'],
            'username': i['Username'],
            'password': i['Password'],
            }
        if i['Hostname'] not in L:
            continue
        cmds=[]
        cmds.append( "router ospf {} \nrouter-id {}".format(i['Process'],i['Router ID'] ))
        for k in i['Networks'].split(' '):
            cmds.append("\nnetwork {} {} area {}".format(get_wmask(k.split(",")[0])[0],get_wmask(k.split(",")[0])[1], k.split(",")[1]))

        shutnoshut = ['int fa1/0', 'sh', 'no sh', 'ip ospf mtu-ignore', 'int fa1/1', 'sh', 'no sh', 'ip ospf mtu-ignore', 'int fa2/0', 'sh', 'no sh', 'ip ospf mtu-ignore']
        cmds.extend(shutnoshut)
        #print(cmds)
        netconnect = ConnectHandler(**cisco)
        op= netconnect.send_config_set(cmds, cmd_verify=False)
        #print(op)
        netconnect.disconnect()
        print("configuration done on: " + i['Hostname'])
        log.write("configuration done on: " + i['Hostname'] + " <br/>")
    return()


# Function to Detect and Resolve SDN Configuration Issues
def sdn_healing():
    log = open("foo.txt", "a")
    nsot = {}
    nsot_act = {}
    count = 1
    with open('nsot_sdn.csv', mode='r') as csv_file:
        cvr = csv.reader(csv_file, delimiter=',')
        for row in cvr:
            if count == 1:
                count = count + 1
                continue
            nsot_act[row[0]] = {}
            nsot_act[row[0]]['Controller IP'] = row[1]
            nsot_act[row[0]]['Openflow Port'] = row[2]
            nsot_act[row[0]]['OF_Version'] = 'OpenFlow' + row[3]

    output= subprocess.check_output("ssh sns@192.168.0.2 sudo ovs-vsctl show", shell=True)
    output = str(output).rstrip()
    op = output.split("Bridge")
    for i in range(1, len(op)):
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', op[i])
        port = re.findall(r'66[5|3]3', op[i])
        opt = op[i].rstrip('\\n')
        p = opt.split()
        p1 = p[0].replace("\"", "")[0:2]
        nsot[p1] = {}
        nsot[p1]['Controller IP'] = ip[0]
        nsot[p1]['Openflow Port'] = port[0]
        output= subprocess.check_output("ssh sns@192.168.0.2 sudo ovs-ofctl show "+p1+" -O OpenFlow13 | grep OFPT_FEATURES_REPLY | awk '{print $2}'", shell=True)
        if 'is_connected:' in op[i]:
            nsot[p1]['Connected'] = 'True'
        else:
            nsot[p1]['Connected'] = 'False'
        if str(output) == "(OF1.3)":
            nsot[p1]['OF_Version'] = 'OpenFlow13'
        else:
            nsot[p1]['OF_Version'] = 'OpenFlow10'
    print("Switches Disconnected:")
    disconnected_list=[]
    for i in nsot.keys():
        if nsot[i]['Connected'] == 'False':
            print(i)
            disconnected_list.append(i)
    print("Disconnected switches--->",disconnected_list)
    log.write("Disconnected switches--->"+ str(disconnected_list) + " <br/>")
    for i in nsot.keys():
        if nsot[i]['Connected'] == 'False':
            if nsot[i]['Controller IP'] != nsot_act[i]['Controller IP'] or nsot[i]['Openflow Port'] != nsot_act[i][
                'Openflow Port']:
                print("Mismatched controller ip on " + i + "\nself healing started")
                log.write("There was an mismatch in the controller ip or port number hence in " + i + " self healing started" + " <br/>")
                subprocess.check_output( 'ssh sns@192.168.0.2 sudo ovs-vsctl set-controller ' + i + ' tcp:' + nsot_act[i]['Controller IP'] + ':' + nsot_act[i][
                        'Openflow Port'], shell=True)
                print("self-healing completed")
            elif nsot[i]['OF_Version'] != nsot_act[i]['OF_Version']:
                print("There was an openflow version mismatch in " + i + " self-healing started")
                log.write("There was an openflow version mismatch in " + i + " self-healing started" + " <br/>")
                out = 'sudo ovs-vsctl set bridge ' + i + ' protocols=' + nsot_act[i]['OF_Version']
                output = subprocess.check_output( 'ssh sns@192.168.0.2 sudo ovs-vsctl set bridge ' + i + ' protocols=' + nsot_act[i]['OF_Version'], shell=True)
                print("self-healing completed")
            else:
                continue
        else:
            if nsot[i]['Openflow Port'] != nsot_act[i]['Openflow Port']:
                print("There is a mismatch in the port number of " + i + " eventhough the switch is connected to the controller self-healing process started")
                log.write("There is a mismatch in the port number of " + i + " eventhough the switch is connected to the controller self-healing process started" + " <br/>")
                output = subprocess.check_output( 'ssh sns@192.168.0.2 sudo ovs-vsctl set-controller ' + i + ' tcp:' + nsot_act[i]['Controller IP'] + ':' + nsot_act[i]['Openflow Port'], shell=True)
                print("self-healing completed")
    log.close()


# Function to Initiate Self_healing for OSPF and SDN
def helper_sf_ospf():
    log = open("foo.txt", "a")
    now = datetime.datetime.now()
    print("Self-healing started at :  <br/>")
    log.write("Self-healing started at :  <br/>")
    print(now.strftime("%Y-%m-%d %H:%M:%S") + " GMT <br/>")
    log.write(now.strftime("%Y-%m-%d %H:%M:%S") + " GMT <br/>")
    log.close()
    p = Process(target= ospf_detect)
    p.start()
    p1 = Process(target= sdn_healing)
    p1.start()

