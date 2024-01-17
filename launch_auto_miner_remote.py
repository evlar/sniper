# launch_auto_miner_remote.py
import argparse
from src.miner_launcher_remote import auto_miner_launcher_remote

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remote Auto Miner Launcher")
    parser.add_argument('--endpoint', required=True, help='Bittensor endpoint')
    args = parser.parse_args()
    auto_miner_launcher_remote(args.endpoint)
