# launch_auto_miner.py 
import argparse
from src.miner_launcher import auto_miner_launcher

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Miner Launcher")
    parser.add_argument('--endpoint', required=True, help='Bittensor endpoint')
    args = parser.parse_args()
    auto_miner_launcher(args.endpoint)
