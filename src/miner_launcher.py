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
CHECK_INTERVAL = 1800  # 30 minutes
PORT_ASSIGNMENTS_FILE = 'data/port_assignments.json'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_available_port(hotkey_name):
    # Extract the numerical identifier from the hotkey name
    _, miner_number = hotkey_name.split('_')
    miner_number = int(miner_number)
    return 9000 + (miner_number - 1)
    
def construct_pm2_command(wallet_name, hotkey_name, axon_port, templates):
    subnet_number = hotkey_name.split('_')[0][1:]
    subnet_template = templates.get(f"subnet{subnet_number}")
    if subnet_template:
        # Expand the path to miner
        path_to_miner = os.path.expanduser(subnet_template["path_to_miner"])

        logging_debug = '--logging.debug' if subnet_template["logging_debug"] else ''
        return [
            'pm2', 'start', path_to_miner, '--name', f"{hotkey_name}_miner",
            '--interpreter', 'python3', '--',
            '--netuid', subnet_number, '--subtensor.network', 'local',
            '--wallet.name', wallet_name, '--wallet.hotkey', hotkey_name,
            '--axon.port', str(axon_port), logging_debug
        ]
    else:
        logging.error(f"Template for subnet{subnet_number} not found.")
        return []
    

def stop_sniper_process(hotkey_name):
    sniper_name = f"sniper_{hotkey_name}"
    subprocess.run(['pm2', 'delete', sniper_name])
    logging.info(f"Stopped PM2 sniper process: {sniper_name}")

def start_mining_for_hotkey(pm2_command):
    if pm2_command:
        subprocess.run(pm2_command)
        logging.info(f"Started mining for hotkey: {pm2_command[6].split('_')[0]} on port {pm2_command[-1]}")




# Helper functions
def read_templates():
    templates_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'miner_pm2_template.json')
    if os.path.exists(templates_path):
        with open(templates_path, 'r') as file:
            return json.load(file)
    return {}



def get_pm2_list():
    result = subprocess.run(['pm2', 'jlist'], stdout=subprocess.PIPE, text=True)
    output = result.stdout.strip()
    if not output:
        logging.error("PM2 jlist returned empty output.")
        return []
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON from PM2 jlist output: {output}")
        return []


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
    
    while True:
        pm2_list = get_pm2_list()
        logging.debug(f"PM2 List: {pm2_list}")  # Log the entire PM2 list for debugging

        for process in pm2_list:
            pm2_name = process.get('name', '')
            logging.debug(f"Processing PM2 process: {pm2_name}")  # Log each process name

            if pm2_name.startswith('sniper_'):
                hotkey_name = pm2_name.split('sniper_')[-1]
                wallet_name = find_wallet_name(hotkey_name)
                hotkey_address = get_hotkey_address(wallet_name, hotkey_name)
                netuid = extract_netuid_from_hotkey(hotkey_name)

                if wallet_name and hotkey_address and netuid is not None:
                    # Use the provided chain_endpoint
                    config = bt.subtensor.config()
                    network = bt_endpoint
                    try:
                        subtensor = bt.subtensor(config=config, network=network)
                    except Exception as e:
                        logging.error(f"Failed to connect to the Subtensor: {e}")
                        continue

                    # Check if the hotkey is registered
                    if is_hotkey_registered(subtensor, hotkey_address, netuid):
                        axon_port = get_available_port(hotkey_name)
                        pm2_command = construct_pm2_command(wallet_name, hotkey_name, axon_port, templates)
                        if pm2_command:
                            logging.info(f"Executing PM2 command: {' '.join(pm2_command)}")
                            start_mining_for_hotkey(pm2_command)
                            stop_sniper_process(hotkey_name)
                    else:
                        logging.warning(f"Hotkey {hotkey_name} is not registered or wallet not found.")

        # Save the current state of PM2 processes after processing
        try:
            subprocess.run(['pm2', 'save'])
            logging.info("PM2 process list saved.")
        except Exception as e:
            logging.error(f"Error saving PM2 process list: {e}")

        time.sleep(CHECK_INTERVAL)
