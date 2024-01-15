# registration_sniper.py

import argparse
import os
import bittensor as bt
from time import sleep
import pexpect
import logging
from logging.handlers import RotatingFileHandler
from getpass import getpass

# Set up argument parsing
parser = argparse.ArgumentParser(description='Run the Bittensor registration sniper.')
parser.add_argument('--wallet-name', required=True, help='Bittensor wallet name')
parser.add_argument('--hotkey-name', required=True, help='Bittensor hotkey name')
parser.add_argument('--wallet-password', required=True, help='Bittensor wallet password')
parser.add_argument('--subtensor', required=True, choices=['local', 'remote'], help='Local or remote subtensor')
parser.add_argument('--endpoint', required=True, help='Bittensor endpoint')
parser.add_argument('--netuid', required=True, help='Bittensor network UID')
parser.add_argument('--threshold', required=True, type=float, help='Registration fee threshold')

args = parser.parse_args()

# Define the log file path
log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'sniper.log')

# Create 'logs' directory if it doesn't exist
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Set logging with RotatingFileHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Use arguments from the command line
bt_wallet_name = args.wallet_name
bt_hotkey_name = args.hotkey_name
bt_cold_pw_wallet = args.wallet_password
subtensor_choice = args.subtensor
bt_endpoint = args.endpoint if subtensor_choice == "remote" else "ws://127.0.0.1:9944"
bt_netuid = args.netuid
registration_fee_threshold = args.threshold

# Hardcoded wallet path
bt_wallet_path = "~/.bittensor/wallets"

# Constants
SLEEP_TIME_SHORT = 10
SLEEP_TIME_LONG = 20

# Set config
config = bt.config()
config.name = bt_wallet_name
config.hotkey = bt_hotkey_name
config.path = bt_wallet_path  # Use the hardcoded path
config.chain_endpoint = bt_endpoint
config.netuid = bt_netuid
config.network = "local" if subtensor_choice == "local" else "remote"
config.no_prompt = True

# Initialize wallet and subtensor
wallet = bt.wallet(config.name, config.hotkey, config.path)
subtensor = bt.subtensor(config.chain_endpoint)
logger.info(f"Wallet: {wallet}")
logger.info(f"Subtensor: {subtensor}")

# Registration loop
while True:
    try:
        current_cost = subtensor.burn(config.netuid)
        logger.info("Current cost: %s", current_cost.tao)
        if current_cost.tao < registration_fee_threshold:
            logger.info(
                "Current registration fee below threshold. Attempting to register..."
            )

            child = pexpect.spawn(
                "python3",
                [
                    "-c",
                    f"""
import bittensor as bt
config = bt.config()
config.name = "{config.name}"
config.hotkey = "{config.hotkey}"
config.path = "{config.path}"
config.chain_endpoint = "{config.chain_endpoint}"
config.netuid = {config.netuid}
config.no_prompt = {config.no_prompt}
wallet = bt.wallet(config.name, config.hotkey, config.path)
subtensor = bt.subtensor(config.chain_endpoint)
try:
    subtensor.burned_register(netuid=config.netuid, wallet=wallet)
except Exception as e:
    print(f"Failed to register neuron: {{e}}")
                    """,
                ],
            )
            child.expect("Enter password to unlock key:")
            child.sendline(bt_cold_pw_wallet)
            child.expect(pexpect.EOF, timeout=None)
            output = child.before.decode()
            logger.info(output)  # Print the output from the command

            if "Registered." in output:
                logger.info("Neuron registered.")
                break
            else:
                logger.info("Registration unsuccessful. Waiting to repeat....")
                sleep(SLEEP_TIME_LONG)
        else:
            logger.info("Current registration fee above threshold.")
            logger.info("Waiting to repeat...")
            sleep(SLEEP_TIME_SHORT)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sleep(SLEEP_TIME_SHORT)

