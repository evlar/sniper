import json
import os
import subprocess
import re

def get_ssh_details():
    with open('data/ssh_details.json', 'r') as file:
        return json.load(file)

def list_servers(ssh_details):
    for key in ssh_details:
        print(f"{key}: {ssh_details[key]['ip_address']}")

def select_server(ssh_details):
    list_servers(ssh_details)
    choice = input("Enter the key of the server to open axon ports: ")
    return ssh_details.get(choice)

def ssh_command(server_details, command):
    host = server_details['ip_address']
    user = server_details['username']
    key_path = server_details['key_path']
    key_path = os.path.expanduser(key_path)
    ssh_cmd = f"ssh -i {key_path} {user}@{host} {command}"
    return subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)

def get_pm2_list(server_details):
    result = ssh_command(server_details, "pm2 jlist")
    try:
        pm2_list = json.loads(result.stdout)
        return pm2_list
    except json.JSONDecodeError:
        print("Failed to decode PM2 list from remote server.")
        return []

def extract_axon_ports(pm2_list):
    axon_ports = set()
    for process in pm2_list:
        args = process.get('pm2_env', {}).get('args', [])
        for i in range(len(args)):
            if args[i] == '--axon.port' and i + 1 < len(args):
                port = args[i + 1]
                axon_ports.add(port)
    return axon_ports

def open_ports_on_remote(server_details, ports):
    for port in ports:
        ssh_command(server_details, f"sudo ufw allow {port}/tcp")

def main():
    ssh_details = get_ssh_details()
    server_details = select_server(ssh_details)
    if server_details:
        pm2_list = get_pm2_list(server_details)
        axon_ports = extract_axon_ports(pm2_list)
        if axon_ports:
            open_ports_on_remote(server_details, axon_ports)
            print(f"Opened axon ports: {', '.join(axon_ports)}")
        else:
            print("No axon ports found to open.")
    else:
        print("Server not found. Please check your input.")

if __name__ == "__main__":
    main()