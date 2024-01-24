# miner_launcher_remote.py
from getpass import getpass
import bittensor as bt
import os
import time
import json
import logging
import subprocess
import paramiko
from .miner_launcher import (
    read_templates, read_sniper_log, update_sniper_process_status, 
    get_available_port, get_hotkey_address, is_hotkey_registered,
    construct_pm2_command, stop_sniper_process
)
from .open_axon_ports import (get_pm2_list, extract_axon_ports, open_ports_on_remote)
# Assuming miner_launcher.py is in the same directory
# If not, adjust the import path accordingly

# Path for the log file
# script_dir = os.path.dirname(os.path.dirname(__file__))
# log_file_path = os.path.join(script_dir, 'logs', 'auto_miner_launcher_remote.log')
SSH_DETAILS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'ssh_details.json')

# Ensure the log directory exists
# os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        #logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

# Constants
CHECK_INTERVAL = 300  # 5 minutes
SSH_DETAILS_FILE = 'data/ssh_details.json'  # Adjust the path as needed


def read_ssh_details():
    with open(SSH_DETAILS_FILE, 'r') as file:
        return json.load(file)

import time  # Ensure this import is at the top of your script



def start_remote_miner(ip_address, username, key_path, pm2_command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    expanded_key_path = os.path.expanduser(key_path)

    try:
        ssh.connect(ip_address, username=username, key_filename=expanded_key_path)

        # Execute the PM2 command (environment variables included)
        full_command = ' '.join(pm2_command)
        stdin, stdout, stderr = ssh.exec_command(full_command)
        logging.info(stdout.read().decode())
        logging.error(stderr.read().decode())

        # Execute 'pm2 save' command
        subprocess.run(['pm2', 'save'])

    except Exception as e:
        logging.error(f"SSH connection error: {e}")
    finally:
        ssh.close()


        
import traceback
'''
def auto_miner_launcher_remote(bt_endpoint, server_name):
    logging.info("Remote Auto Miner Launcher started.")
    templates = read_templates()
    ssh_details = read_ssh_details()

    # Read the sniper_processes.log file to get the active sniper processes and their subnet numbers
    sniper_processes = read_sniper_log()
    active_subnets = {details['netuid'] for _, details in sniper_processes if details['status'] == 'active' and details['endpoint'] == bt_endpoint}

    for subnet in active_subnets:
        try:
            if server_name is None:
                # If multiple servers are found for the subnet and no specific server name is provided
                if len(ssh_details.get(f"subnet{subnet}", [])) > 1:
                    print(f"Multiple servers found for subnet {subnet}:")
                    for i, server in enumerate(ssh_details[f"subnet{subnet}"], start=1):
                        print(f"{i}. {server['server_name']}")
                    server_choice = input("Select the server number to use: ")
                    server_name = ssh_details[f"subnet{subnet}"][int(server_choice) - 1]['server_name']

            # Find the server details by server_name
            server_details = next((server for server in ssh_details.get(f"subnet{subnet}", []) if server['server_name'] == server_name), None)
            if not server_details:
                logging.error(f"No server details found for server {server_name} on subnet {subnet}.")
                continue  # Skip to the next subnet if no server details are found

            # Create a Subtensor instance
            config = bt.subtensor.config()
            subtensor = bt.subtensor(config=config, network=bt_endpoint)

            # Process sniper processes for the current subnet
            for pm2_name, details in sniper_processes:
                if details['status'] == 'active' and details['endpoint'] == bt_endpoint and details['netuid'] == subnet:
                    hotkey_name = details['hotkey_name']
                    wallet_name = details['wallet_name']
                    axon_port = get_available_port(hotkey_name)

                    hotkey_address = get_hotkey_address(wallet_name, hotkey_name)
                    if is_hotkey_registered(subtensor, hotkey_address, subnet):
                        # Construct the PM2 command with local=False for remote execution
                        pm2_command = construct_pm2_command(wallet_name, hotkey_name, axon_port, templates, local=False)

                        if pm2_command:
                            logging.info(f"Executing remote PM2 command: {' '.join(pm2_command)}")
                            start_remote_miner(server_details['ip_address'], server_details['username'], server_details['key_path'], pm2_command)
                            stop_sniper_process(pm2_name)
                            update_sniper_process_status(pm2_name, "stopped")

                            # Open axon ports
                            pm2_list = get_pm2_list(server_details)
                            axon_ports = extract_axon_ports(pm2_list)
                            open_ports_on_remote(server_details, axon_ports)

                        else:
                            logging.warning(f"PM2 command not generated for {hotkey_name}.")
                    else:
                        logging.info(f"Hotkey {hotkey_name} is not yet registered. Skipping.")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            logging.debug(traceback.format_exc())  # Log the full traceback

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)
'''

'''
def auto_miner_launcher_remote(bt_endpoint, server_name=None):
    logging.info("Remote Auto Miner Launcher started.")
    templates = read_templates()
    ssh_details = read_ssh_details()

    # Read the sniper_processes.log file to get the active sniper processes and their subnet numbers
    sniper_processes = read_sniper_log()
    active_subnets = {details['netuid'] for _, details in sniper_processes if details['status'] == 'active' and details['endpoint'] == bt_endpoint}

    # If server_name is not provided, prompt the user to select one
    for subnet in active_subnets:
        if server_name is None and len(ssh_details.get(f"subnet{subnet}", [])) > 1:
            print(f"Multiple servers found for subnet {subnet}:")
            for i, server in enumerate(ssh_details[f"subnet{subnet}"], start=1):
                print(f"{i}. {server['server_name']}")
            server_choice = input("Select the server number to use: ")
            server_name = ssh_details[f"subnet{subnet}"][int(server_choice) - 1]['server_name']

        # Find the server details by server_name
        server_details = next((server for server in ssh_details.get(f"subnet{subnet}", []) if server['server_name'] == server_name), None)
        if not server_details:
            logging.error(f"No server details found for server {server_name} on subnet {subnet}.")
            continue  # Skip to the next subnet if no server details are found


    # If server_name is not provided, prompt the user to select one
    if server_name is None and len(ssh_details.get(f"subnet{subnet}", [])) > 1:
        print(f"Multiple servers found for subnet {subnet}:")
        for i, server in enumerate(ssh_details[f"subnet{subnet}"], start=1):
            print(f"{i}. {server['server_name']}")
        server_choice = input("Select the server number to use: ")
        server_name = ssh_details[f"subnet{subnet}"][int(server_choice) - 1]['server_name']

    # Find the server details by server_name
    server_details = next((server for server in ssh_details.get(subnet, []) if server['server_name'] == server_name), None)
    if not server_details:
        logging.error(f"No server details found for server {server_name} on subnet {subnet}.")
        return

    # Create a Subtensor instance
    config = bt.subtensor.config()
    try:
        subtensor = bt.subtensor(config=config, network=bt_endpoint)
    except Exception as e:
        logging.error(f"Failed to connect to the Subtensor: {e}")
        logging.debug(traceback.format_exc())  # Log the full traceback
        return  # Exit the function if unable to connect

    while True:
        try:
            sniper_processes = read_sniper_log()
            logging.debug(f"Read {len(sniper_processes)} sniper processes from log.")

            for pm2_name, details in sniper_processes:
                logging.debug(f"Processing PM2 process: {pm2_name} with details: {details}")

                if details['status'] == 'active' and details['endpoint'] == bt_endpoint:
                    hotkey_name = details['hotkey_name']
                    wallet_name = details['wallet_name']
                    netuid = details['netuid']
                    axon_port = get_available_port(hotkey_name)

                    hotkey_address = get_hotkey_address(wallet_name, hotkey_name)
                    if is_hotkey_registered(subtensor, hotkey_address, netuid):
                        # Construct the PM2 command with local=False for remote execution
                        pm2_command = construct_pm2_command(wallet_name, hotkey_name, axon_port, templates, local=False)

                        if pm2_command:
                            logging.info(f"Executing remote PM2 command: {' '.join(pm2_command)}")
                            start_remote_miner(server_details['ip_address'], server_details['username'], server_details['key_path'], pm2_command)
                            stop_sniper_process(pm2_name)
                            update_sniper_process_status(pm2_name, "stopped")

                            # Open axon ports
                            pm2_list = get_pm2_list(server_details)
                            axon_ports = extract_axon_ports(pm2_list)
                            open_ports_on_remote(server_details, axon_ports)

                        else:
                            logging.warning(f"PM2 command not generated for {hotkey_name}.")
                    else:
                        logging.info(f"Hotkey {hotkey_name} is not yet registered. Skipping.")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            logging.debug(traceback.format_exc())  # Log the full traceback

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)
'''

def auto_miner_launcher_remote(bt_endpoint, server_name):
    logging.info("Remote Auto Miner Launcher started.")
    templates = read_templates()
    ssh_details = read_ssh_details()

    # Create a Subtensor instance
    config = bt.subtensor.config()
    try:
        subtensor = bt.subtensor(config=config, network=bt_endpoint)
    except Exception as e:
        logging.error(f"Failed to connect to the Subtensor: {e}")
        logging.debug(traceback.format_exc())  # Log the full traceback
        return  # Exit the function if unable to connect

    while True:
        try:
            sniper_processes = read_sniper_log()
            logging.debug(f"Read {len(sniper_processes)} sniper processes from log.")

            for pm2_name, details in sniper_processes:
                logging.debug(f"Processing PM2 process: {pm2_name} with details: {details}")

                if details['status'] == 'active' and details['endpoint'] == bt_endpoint:
                    hotkey_name = details['hotkey_name']
                    wallet_name = details['wallet_name']
                    netuid = details['netuid']
                    axon_port = get_available_port(hotkey_name)

                    hotkey_address = get_hotkey_address(wallet_name, hotkey_name)
                    if is_hotkey_registered(subtensor, hotkey_address, netuid):
                        # Construct the PM2 command with local=False for remote execution
                        pm2_command = construct_pm2_command(wallet_name, hotkey_name, axon_port, templates, local=False)

                        if pm2_command:
                            # Use the provided server_name to find the server details
                            server_details = next((server for server in ssh_details.get(f"subnet{netuid}", []) if server['server_name'] == server_name), None)
                            if server_details:
                                logging.info(f"Executing remote PM2 command: {' '.join(pm2_command)}")
                                start_remote_miner(server_details['ip_address'], server_details['username'], server_details['key_path'], pm2_command)
                                stop_sniper_process(pm2_name)
                                update_sniper_process_status(pm2_name, "stopped")

                                # Open axon ports
                                pm2_list = get_pm2_list(server_details)
                                axon_ports = extract_axon_ports(pm2_list)
                                open_ports_on_remote(server_details, axon_ports)
                            else:
                                logging.warning(f"No server details found for server {server_name} on subnet {netuid}. Cannot start remote miner.")
                        else:
                            logging.warning(f"PM2 command not generated for {hotkey_name}.")
                    else:
                        logging.info(f"Hotkey {hotkey_name} is not yet registered. Skipping.")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            logging.debug(traceback.format_exc())  # Log the full traceback

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)


'''
################ from origin main ##########################
def auto_miner_launcher_remote(bt_endpoint,):
    logging.info("Remote Auto Miner Launcher started.")
    templates = read_templates()
    ssh_details = read_ssh_details()

    # Create a Subtensor instance
    config = bt.subtensor.config()
    try:
        subtensor = bt.subtensor(config=config, network=bt_endpoint)
    except Exception as e:
        logging.error(f"Failed to connect to the Subtensor: {e}")
        logging.debug(traceback.format_exc())  # Log the full traceback
        return  # Exit the function if unable to connect

    while True:
        try:
            sniper_processes = read_sniper_log()
            logging.debug(f"Read {len(sniper_processes)} sniper processes from log.")

            for pm2_name, details in sniper_processes:
                logging.debug(f"Processing PM2 process: {pm2_name} with details: {details}")

                if details['status'] == 'active' and details['endpoint'] == bt_endpoint:
                    hotkey_name = details['hotkey_name']
                    wallet_name = details['wallet_name']
                    netuid = details['netuid']
                    axon_port = get_available_port(hotkey_name)

                    hotkey_address = get_hotkey_address(wallet_name, hotkey_name)
                    if is_hotkey_registered(subtensor, hotkey_address, netuid):
                        # Construct the PM2 command with local=False for remote execution
                        pm2_command = construct_pm2_command(wallet_name, hotkey_name, axon_port, templates, local=False)

                        if pm2_command:
                            subnet = f"subnet{netuid}"
                            if subnet in ssh_details:
                                ssh_info = ssh_details[subnet]
                                logging.info(f"Executing remote PM2 command: {' '.join(pm2_command)}")
                                start_remote_miner(ssh_info['ip_address'], ssh_info['username'], ssh_info['key_path'], pm2_command)
                                stop_sniper_process(pm2_name)
                                update_sniper_process_status(pm2_name, "stopped")

                                # Open axon ports
                                pm2_list = get_pm2_list(ssh_info)
                                axon_ports = extract_axon_ports(pm2_list)
                                open_ports_on_remote(ssh_info, axon_ports)

                            else:
                                logging.warning(f"No SSH details found for {subnet}. Cannot start remote miner.")
                        else:
                            logging.warning(f"PM2 command not generated for {hotkey_name}.")
                    else:
                        logging.info(f"Hotkey {hotkey_name} is not yet registered. Skipping.")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            logging.debug(traceback.format_exc())  # Log the full traceback

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)
'''

def clear_sniper_log():
    script_dir = os.path.dirname(os.path.dirname(__file__))
    log_file_path = os.path.join(script_dir, 'logs', 'sniper_processes.log')
    with open(log_file_path, 'w') as file:
        file.write('')  # Clear the log file

