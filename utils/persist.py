import argparse
import csv
import os
import sys
from datetime import date, timedelta

fieldnames = [
  'wg_internal_client_name',
  'wg_peer_ip_addr',
  'created_date',
  'expected_expire_date'
]

def create(user_email_addr: str, client_name: str, peer_addr: str):
    user_name = user_email_addr.partition("@")[0]
    file_path = os.getcwd() + "/accounts-storage/active/" + user_name + ".csv"
    today = date.today()

    file_exists = os.path.isfile(file_path)
    mode = 'a' if file_exists else 'w'
    with open(file_path, mode, newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
          writer.writeheader()
        writer.writerow({
          'wg_internal_client_name': client_name,
          'wg_peer_ip_addr': peer_addr,
          'created_date': today,
          'expected_expire_date': today + timedelta(days=90)
        })
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user-email-addr', '-u', dest='user_email_addr', required=True)
    parser.add_argument('--client-name', '-c', dest='client_name')
    parser.add_argument('--peer-addr', '-p', dest='peer_addr')
    parser.add_argument('--operation', dest='operation', help="create, remove")
    options = parser.parse_args()

    if options.operation == "create":
        if options.client_name is None:
            print("--client-name is required for operation: create")
            sys.exit(1)
        if options.peer_addr is None:
            print("--peer-addr is required for operation: create")
            sys.exit(1)
        create(options.user_email_addr, options.client_name, options.peer_addr)
    elif options.operation == "remove":
        pass
    else:
        print("Unrecognized operation: " + options.operation)
        sys.exit(1)
