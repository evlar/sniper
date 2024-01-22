# launch_auto_miner_remote.py
import argparse
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.miner_launcher_remote import auto_miner_launcher_remote

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote Auto Miner Launcher")
    parser.add_argument('--endpoint', required=True, help='Bittensor endpoint')
    parser.add_argument('--server-name', required=False, help='Server name for the remote miner', default=None)
    args = parser.parse_args()
    auto_miner_launcher_remote(args.endpoint, args.server_name)