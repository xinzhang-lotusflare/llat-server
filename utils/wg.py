#
#  A cli wrapper for wireguard-install.sh
#

import argparse
import os
import pty
import sys
import re

LF_DNS = "10.8.0.1"
GOOGLE_DNS = "8.8.8.8"

WAIT_FOR_OPTIONS = 0
FINISH = 999
state = WAIT_FOR_OPTIONS

def finish_input(fd):
    os.write(fd, b"\n")

def add_client(client_name): 
    WAIT_FOR_NAME = 1
    WAIT_FOR_PRIMARY_DNS_SELECT_DNS = 2
    WAIT_FOR_PRIMARY_DNS = 3
    WAIT_FOR_SECONDARY_DNS = 4
    def execute(fd):
        global state
        data = os.read(fd, 1024)
        if state == WAIT_FOR_OPTIONS:
            if data.endswith(b"Option: "):
                os.write(fd, b"1")
                finish_input(fd)
                state = WAIT_FOR_NAME
        elif state == WAIT_FOR_NAME:
            if data.endswith(b"Name: "):
                os.write(fd, bytes(client_name, encoding="utf-8"))
                finish_input(fd)
                state = WAIT_FOR_PRIMARY_DNS_SELECT_DNS
        elif state == WAIT_FOR_PRIMARY_DNS_SELECT_DNS:
            if data.endswith(b"Name: "):
                print("Duplicated client name")
                sys.exit(1)
            elif data.endswith(b"DNS server [2]: "):
                os.write(fd, b"7")
                finish_input(fd)
                state = WAIT_FOR_PRIMARY_DNS        
        elif state == WAIT_FOR_PRIMARY_DNS:
            if data.endswith(b"Enter primary DNS server: "):
                os.write(fd, bytes(LF_DNS, encoding="utf-8"))
                finish_input(fd)
                state = WAIT_FOR_SECONDARY_DNS          
        elif state == WAIT_FOR_SECONDARY_DNS:
            if data.endswith(b"Enter secondary DNS server (Enter to skip): "):
                os.write(fd, bytes(GOOGLE_DNS, encoding="utf-8"))
                finish_input(fd)
                state = FINISH        
        return data
    return execute

CLIENT_INDEX = "-1"
RAW_CLIENT_LIST = b''
def list_clients():
    WAIT_FOR_CLIENT_LIST = 1
    def execute(fd):
        global state, RAW_CLIENT_LIST
        data = os.read(fd, 1024)
        if state == WAIT_FOR_OPTIONS:
            if data.endswith(b"Option: "):
                os.write(fd, b"2")
                finish_input(fd)
                state = WAIT_FOR_CLIENT_LIST
        elif state == WAIT_FOR_CLIENT_LIST:
            RAW_CLIENT_LIST += data
        return data
    return execute
    
def search_client(target):
    global RAW_CLIENT_LIST
    splitted = RAW_CLIENT_LIST.split(b"\r\n")
    started_with_number = r'^\s*\d{1,}\)'
    for part in splitted:
        p = str(part, encoding="utf-8")
        match = re.search(started_with_number, p)
        if match:
            client_name = p.split(")")[1].strip()
            if client_name == target:
                index = match.group(0).split(")")[0].strip()
                return index
    print("Cannot find client: " + target)
    sys.exit(1)

def rm_client(client_index):
    WAIT_FOR_CLIENT_INDEX = 1
    WAIT_FOR_CONFIRM = 2
    def execute(fd):
        global state
        data = os.read(fd, 1024)
        if state == WAIT_FOR_OPTIONS:
            if data.endswith(b"Option: "):
                os.write(fd, b"3")
                finish_input(fd)
                state = WAIT_FOR_CLIENT_INDEX
        elif state == WAIT_FOR_CLIENT_INDEX:
            if data.endswith(b"Client: "):
                os.write(fd, bytes(client_index, encoding="utf-8"))
                finish_input(fd)
                state = WAIT_FOR_CONFIRM
        elif state == WAIT_FOR_CONFIRM:
            if data.endswith(b"removal? [y/N]: "):
                os.write(fd, b"y")
                finish_input(fd)
                state = WAIT_FOR_CONFIRM        
        return data
    return execute

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--wg-script', '-s', dest='wg_script', required=True)
    parser.add_argument('--client-name', '-c', dest='client_name', required=True)
    parser.add_argument('operation', help="add or rm")
    options = parser.parse_args()

    if options.operation == 'add':
        pty.spawn(options.wg_script, add_client(options.client_name))
    elif options.operation == 'rm':
        pty.spawn(options.wg_script, list_clients())
        index = search_client(options.client_name)
        print("Find client at index: " + index)
        state = WAIT_FOR_OPTIONS
        pty.spawn(options.wg_script, rm_client(index))
    else:
        print("Unsupported operation: " + options.operation) 
        sys.exit(1)

