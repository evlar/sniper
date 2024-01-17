# miner_launcher.py
import subprocess
import bittensor as bt
import os
import time
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
import argparse

# Path for the log file
log_file_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'auto_miner_launcher.log')

# Create 'logs' directory if it doesn't exist
logs_dir = os.path.dirname(log_file_path)
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Setup logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5),
        logging.StreamHandler()
    ]
)

# Constants
CHECK_INTERVAL = 300  # 5 minutes
PORT_ASSIGNMENTS_FILE = 'data/port_assignments.json'



# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_available_port(hotkey_name):
    # Extract the numerical identifier from the hotkey name
    _, miner_number = hotkey_name.split('_')
    miner_number = int(miner_number)
    return 9000 + (miner_number - 1)
    
def construct_pm2_command(wallet_name, hotkey_name, axon_port, templates, local=True):
    subnet_number = hotkey_name.split('_')[0][1:]
    subnet_template = templates.get(f"subnet{subnet_number}")

    if subnet_template:
        # Get the path to miner and expand it if necessary
        path_to_miner = subnet_template["path_to_miner"]
        
        if local:
            # Resolve path for local environment
            if path_to_miner.startswith("~/"):
                path_to_miner = os.path.expanduser(path_to_miner)
            elif not os.path.isabs(path_to_miner):
                script_dir = os.path.dirname(os.path.dirname(__file__))
                path_to_miner = os.path.join(script_dir, path_to_miner)
        else:
            # For remote environment, assume the path is correct as is or needs special handling
            # Specific logic for remote path resolution (if needed) goes here
            pass  # Placeholder for potential future logic

        # Start building the command
        command = [
            'pm2', 'start', path_to_miner, '--name', f"{hotkey_name}_miner",
            '--interpreter', 'python3', '--',
            '--netuid', subnet_number, '--subtensor.network', 'local',
            '--wallet.name', wallet_name, '--wallet.hotkey', hotkey_name,
            '--axon.port', str(axon_port)
        ]

        # Add additional parameters from the template
        additional_params = subnet_template.get("additional_params", {})
        for param, value in additional_params.items():
            command.extend([f"--{param}", value])

        # Add logging debug if applicable at the end
        if subnet_template.get("logging_debug", False):
            command.append('--logging.debug')

        return command
    else:
        logging.error(f"Template for subnet{subnet_number} not found.")
        return []





    

def stop_sniper_process(pm2_name):
    subprocess.run(['pm2', 'delete', pm2_name])
    logging.info(f"Stopped PM2 sniper process: {pm2_name}")

#def start_mining_for_hotkey(pm2_command):
#    if pm2_command:
#        subprocess.run(pm2_command)
#        logging.info(f"Started mining for hotkey: {pm2_command[6].split('_')[0]} on port {pm2_command[-1]}")


def start_mining_for_hotkey(pm2_command):
    if pm2_command:
        # Start the PM2 process
        subprocess.run(pm2_command)
        hotkey = pm2_command[6].split('_')[0]  # Assuming hotkey name is the 7th element in the command
        port = pm2_command[-1]  # Assuming port number is the last element in the command
        logging.info(f"Started mining for hotkey: {hotkey} on port {port}")

        # Wait for 30 seconds before restarting
        time.sleep(30)

        # Restart the same process with --update-env
        restart_command = ['pm2', 'restart', f"{hotkey}_miner", '--update-env']
        subprocess.run(restart_command)
        logging.info(f"Restarted mining for hotkey: {hotkey} with --update-env on port {port}")



# Helper functions
def read_templates():
    templates_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'miner_pm2_template.json')
    if os.path.exists(templates_path):
        with open(templates_path, 'r') as file:
            return json.load(file)
    return {}

#def get_pm2_list():
#    result = subprocess.run(['pm2', 'jlist'], stdout=subprocess.PIPE, text=True)
#    output = result.stdout.strip()
#    if not output:
#        logging.error("PM2 jlist returned empty output.")
#        return []
#    try:
#        return json.loads(output)
#    except json.JSONDecodeError:
#        logging.error(f"Failed to decode JSON from PM2 jlist output: {output}")
#        return []

def read_sniper_log():
    # Path one level up from the current script directory
    script_dir = os.path.dirname(os.path.dirname(__file__))
    
    log_file_path = os.path.join(script_dir, 'logs', 'sniper_processes.log')
    
    try:
        with open(log_file_path, 'r') as log_file:
            sniper_process_lines = log_file.readlines()

        # Parsing each line to extract JSON data
        parsed_log = []
        for line in sniper_process_lines:
            try:
                # Split line into pm2_name and json_str, then parse the JSON
                pm2_name, json_str = line.split(': ', 1)
                json_data = json.loads(json_str.strip())
                parsed_log.append((pm2_name, json_data))
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from log line: {e}")
            except ValueError:
                logging.error(f"Error splitting log line: {line}")

        return parsed_log
    except FileNotFoundError:
        logging.error("Sniper process log file not found.")
        return []
    
def update_sniper_process_status(pm2_name, new_status):
    script_dir = os.path.dirname(os.path.dirname(__file__))
    log_file_path = os.path.join(script_dir, 'logs', 'sniper_processes.log')

    try:
        with open(log_file_path, 'r') as file:
            log_entries = file.readlines()

        updated_entries = []
        for entry in log_entries:
            name, json_str = entry.split(':', 1)
            if name.strip() == pm2_name:
                details = json.loads(json_str)
                details["status"] = new_status
                updated_entries.append(f"{name}: {json.dumps(details)}\n")
            else:
                updated_entries.append(entry)

        # Write the updated log back to the file
        with open(log_file_path, 'w') as file:
            file.writelines(updated_entries)

    except FileNotFoundError:
        logging.error("Sniper process log file not found.")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from log file: {e}")
    except Exception as e:
        logging.error(f"An error occurred updating the log file: {e}")

def read_port_assignments():
    port_assignments_path = os.path.join(os.path.dirname(__file__), '..', PORT_ASSIGNMENTS_FILE)
    if os.path.exists(port_assignments_path):
        with open(port_assignments_path, 'r') as file:
            return json.load(file)
    return {}

def find_wallet_name(hotkey_name):
    wallets_path = os.path.expanduser('~/.bittensor/wallets/')
    for wallet_name in os.listdir(wallets_path):
        hotkeys_path = os.path.join(wallets_path, wallet_name, 'hotkeys')
        if os.path.isdir(hotkeys_path) and hotkey_name in os.listdir(hotkeys_path):
            return wallet_name
    return None

def get_neuron_info_for_hotkey(subtensor: "bt.subtensor", hotkey: str, netuid: int) -> Optional["bt.NeuronInfoLite"]:
    """
    Fetches neuron information for a specific hotkey.
    
    Args:
        subtensor (bittensor.subtensor): An instance of the subtensor object.
        hotkey (str): The SS58 address of the hotkey.
        netuid (int): The network UID to query.

    Returns:
        bittensor.NeuronInfoLite: Neuron information, or None if not found.
    """
    try:
        all_neurons = subtensor.neurons_lite(netuid=netuid)
        neuron_info = next((neuron for neuron in all_neurons if neuron.hotkey == hotkey), None)
        return neuron_info
    except Exception as e:
        print(f"Error while fetching neuron info: {e}")
        return None


def is_hotkey_registered(subtensor, hotkey_address, netuid):
    try:
        neuron_info = get_neuron_info_for_hotkey(subtensor, hotkey_address, netuid)
        return neuron_info is not None
    except Exception as e:
        logging.error(f"Error checking registration status: {e}")
        return False
    
def get_hotkey_address(wallet_name, hotkey_name):
    hotkey_file_path = os.path.expanduser(f'~/.bittensor/wallets/{wallet_name}/hotkeys/{hotkey_name}')
    if os.path.exists(hotkey_file_path):
        with open(hotkey_file_path, 'r') as file:
            hotkey_data = json.load(file)
            return hotkey_data.get("ss58Address", "")
    else:
        logging.error(f"Hotkey file not found: {hotkey_file_path}")
        return None

def extract_netuid_from_hotkey(hotkey_name):
    parts = hotkey_name.split('_')
    if len(parts) > 1 and parts[0].startswith('s'):
        return int(parts[0][1:])
    else:
        logging.error("Invalid hotkey name format for extracting netuid")
        return None   


def auto_miner_launcher(bt_endpoint):
    logging.info("Auto Miner Launcher started.")
    templates = read_templates()

    all_processed = True


    # Create a Subtensor instance
    config = bt.subtensor.config()
    try:
        subtensor = bt.subtensor(config=config, network=bt_endpoint)
    except Exception as e:
        logging.error(f"Failed to connect to the Subtensor: {e}")
        return  # Exit the function if unable to connect

    all_processed = True  # Variable to track if all sniper processes are processed

    while True:
        sniper_processes = read_sniper_log()
        logging.debug(f"Read {len(sniper_processes)} sniper processes from log.")

        for pm2_name, details in sniper_processes:
            logging.debug(f"Processing PM2 process: {pm2_name} with details: {details}")

            if details['endpoint'] == bt_endpoint and details['status'] == 'active':
                hotkey_name = details['hotkey_name']
                wallet_name = details['wallet_name']
                netuid = details['netuid']
                axon_port = get_available_port(hotkey_name)

                hotkey_address = get_hotkey_address(wallet_name, hotkey_name)
                if is_hotkey_registered(subtensor, hotkey_address, netuid):
                    pm2_command = construct_pm2_command(wallet_name, hotkey_name, axon_port, templates)

                    if pm2_command:
                        logging.info(f"Executing PM2 command: {' '.join(pm2_command)}")
                        start_mining_for_hotkey(pm2_command, hotkey_name)
                        stop_sniper_process(pm2_name)
                        update_sniper_process_status(pm2_name, "stopped")
                    else:
                        all_processed = False  # Mark as not processed if PM2 command is not generated
                        logging.warning(f"PM2 command not generated for {hotkey_name}.")
                else:
                    all_processed = False  # Mark as not processed if any hotkey is not registered
                    logging.info(f"Hotkey {hotkey_name} is not yet registered. Skipping.")
            else:
                logging.debug(f"Skipping inactive or unrelated process: {pm2_name}")

        if all_processed:
            # All processes have been processed, so stop the auto_miner_launcher and clear the log
            logging.info("All sniper processes have been processed. Stopping auto_miner_launcher and clearing log.")
            subprocess.run(['pm2', 'delete', 'auto_miner_launcher'])
            clear_sniper_log()
            break

        # Save the current state of PM2 processes after processing
        try:
            subprocess.run(['pm2', 'save'])
            logging.info("PM2 process list saved.")
        except Exception as e:
            logging.error(f"Error saving PM2 process list: {e}")

        # Wait before the next check
        time.sleep(CHECK_INTERVAL)

def clear_sniper_log():
    script_dir = os.path.dirname(os.path.dirname(__file__))
    log_file_path = os.path.join(script_dir, 'logs', 'sniper_processes.log')
    with open(log_file_path, 'w') as file:
        file.write('')  # Clear the log file
