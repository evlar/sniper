# miner_launcher_remote.py
from getpass import getpass
import bittensor as bt
import os
import time
import json
import logging
import paramiko
from .miner_launcher import (
    read_templates, read_sniper_log, update_sniper_process_status, 
    get_available_port, get_hotkey_address, is_hotkey_registered,
    construct_pm2_command, stop_sniper_process
)

# Assuming miner_launcher.py is in the same directory
# If not, adjust the import path accordingly

# Path for the log file
script_dir = os.path.dirname(os.path.dirname(__file__))
log_file_path = os.path.join(script_dir, 'logs', 'auto_miner_launcher_remote.log')
SSH_DETAILS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'ssh_details.json')

# Ensure the log directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)


# Constants
CHECK_INTERVAL = 300  # 5 minutes
SSH_DETAILS_FILE = 'data/ssh_details.json'  # Adjust the path as needed


def read_ssh_details():
    with open(SSH_DETAILS_FILE, 'r') as file:
        return json.load(file)

def start_remote_miner(ip_address, username, key_path, pm2_command, hotkey_name):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    expanded_key_path = os.path.expanduser(key_path)

    try:
        ssh.connect(ip_address, username=username, key_filename=expanded_key_path)

        # Execute the PM2 start command
        stdout, stderr = ssh.exec_command(' '.join(pm2_command))[:2]
        logging.info(stdout.read().decode())
        logging.error(stderr.read().decode())

        # Construct the PM2 restart command with --update-env
        restart_command = f'pm2 restart {hotkey_name}_miner --update-env'
        stdout, stderr = ssh.exec_command(restart_command)[:2]
        logging.info(f"Restarting {hotkey_name}_miner with --update-env")
        logging.info(stdout.read().decode())
        logging.error(stderr.read().decode())

    except Exception as e:
        logging.error(f"SSH connection error: {e}")
    finally:
        ssh.close()

# sniper process occurs locally, so we need to use the local pm2 to stop it, or call in the 'stop_sniper_process' function from miner_launcher.py
#def stop_remote_sniper_process(ip_address, username, key_path, pm2_name):
#    stop_command = ['pm2', 'delete', pm2_name]
#    start_remote_miner(ip_address, username, key_path, stop_command)
################################################################################################################################################

def auto_miner_launcher_remote(bt_endpoint):
    logging.info("Remote Auto Miner Launcher started.")
    templates = read_templates()
    ssh_details = read_ssh_details()

    # Create a Subtensor instance
    config = bt.subtensor.config()
    try:
        subtensor = bt.subtensor(config=config, network=bt_endpoint)
    except Exception as e:
        logging.error(f"Failed to connect to the Subtensor: {e}")
        return  # Exit the function if unable to connect

    while True:
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
                            start_remote_miner(ssh_info['ip_address'], ssh_info['username'], ssh_info['key_path'], pm2_command, hotkey_name)
                            stop_sniper_process(pm2_name)
                            update_sniper_process_status(pm2_name, "stopped")
                        else:
                            logging.warning(f"No SSH details found for {subnet}. Cannot start remote miner.")
                    else:
                        logging.warning(f"PM2 command not generated for {hotkey_name}.")
                else:
                    logging.info(f"Hotkey {hotkey_name} is not yet registered. Skipping.")
            else:
                logging.debug(f"Skipping inactive or unrelated process: {pm2_name}")

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)



def clear_sniper_log():
    script_dir = os.path.dirname(os.path.dirname(__file__))
    log_file_path = os.path.join(script_dir, 'logs', 'sniper_processes.log')
    with open(log_file_path, 'w') as file:
        file.write('')  # Clear the log file

