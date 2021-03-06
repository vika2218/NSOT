import csv
from netmiko import ConnectHandler
import os
from intent import *
import subprocess
import json
import requests
import time


# Function to Read CSV File
def read_csv():
    csvfile = open('nsot_tn.csv', 'r')
    fieldnames = ("Hostname","Management IP","Username","Password","Router ID","Process", "Networks")
    reader = csv.DictReader( csvfile, fieldnames)
    return(reader)


# Function to Test Reachability of Management IPs
def reachability_test():
    j = read_csv()
    for i in j:
        op= (os.system("ping {} -c 1 -t 2".format(i['Management IP'])))
        print("op is --> {}".format(op))
        if op != 0:
            return str(1)
    else:
        return str(0)


# Function to Test Configuration of Hostname Intent
def host():
    j = read_csv()
    results = ''
    for i in j:
        a = hostname(**i)
        #print(a)
        if a == i['Hostname']:
            results = results + ' ' + i['Hostname'] + ':Pass,'
        else:
            results = results + ' ' + i['Hostname'] + ':Fail,'
    print(results)
    return results


# Function to Get DPIDs
def get_dpid():
    filename = "nsot_sdn.csv" ###
    dpid_list = []
    fieldnames = ("DPID", "Management IP", "Username", "Password")
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile,fieldnames)
        for row in reader:
            if row['DPID'] == 'Hostname':
                continue
            dpid_list.append(row['DPID'][1])
        print("DPID: {}".format(dpid_list) )
    return dpid_list


# Function to Get Number of Flow Entries Installed
def get_flow_entries(dpid):
    r= requests.get("http://192.168.0.3:8080/stats/flow/{}" .format(dpid))
    for switch,flow_entries in r.json().items():
        number = len(flow_entries)
    return number


# Function to Test PushFlowEntries Intent
def flow_test():
    dpid_list = get_dpid()
    dpid_dict_before_push = {}
    dpid_dict_after_push = {}

    for dpid in dpid_list:
        # number of flow-entries before pushing the entries from csv = number_1
        dpid_dict_before_push.update({ dpid : get_flow_entries(dpid) } )
        # dpid_dict_before_push[dpid].append(get_flow_entries(dpid))

    print(dpid_dict_before_push)

    sdn_intent()
    for dpid in dpid_list:
        # number of flow-entries after pushing the entries from csv = number_2
        dpid_dict_after_push.update({ dpid : get_flow_entries(dpid) } )
        # dpid_dict_after_push[dpid].append(get_flow_entries(dpid))
    print(dpid_dict_after_push)

