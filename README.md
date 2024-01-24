
# README.md for registration_sniper

## Project Overview

"registration_sniper" is a Python-based tool designed for the Bittensor network. It automates the process of registering neurons when the fee falls below a threshold, launches miners automatically, and manages subtensor endpoints and wallet configurations. The project is structured with a clear separation of concerns, making it easy to maintain and extend.

## Features

- **Registration Sniper**: Monitors registration fees and registers neurons when the fee is affordable.
- **Auto Miner Launcher**: Automates the launching of miners for different hotkeys and subnets, both locally and remotely, with environment variable configuration.
- **Subtensor Endpoint Management**: Handles local and remote subtensor endpoints, allowing users to switch between them easily.
- **Wallet and Hotkey Management**: Manages Bittensor wallets and hotkeys, ensuring secure and efficient operations.

## Installation

To set up the "registration_sniper" project, follow these steps:

1. Clone the repository to your local machine.
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Ensure PM2 is installed on your system for process management.
   ```
   sudo apt install npm -y && sudo npm install pm2@latest -g && pm2 update
   ```
## Usage

1. **Run the Application**:
   ```
   python3 run.py
   ```
   This will launch the main menu, providing options to manage registration snipers and auto miner launchers.

2. **Main Menu Options**:
   1. `PM2 Launch Command and Environment Variable Configuration:` This option allows the user to save command templates including environment variables for launching miners on different subnets using PM2.
   2. `Server Details Configuration:` This option is for saving SSH details for remote miner launching.
               [Click here](docs/sniper_setup_guide.md) for more information on setup for options 1 and 2.

   3. `Registration Sniper:` This option runs a registration sniper process for registering on a specified subnet.
   4. `Auto Miner Launcher (remotely):` This automatically launches miners for newly detected registered hotkeys on your remote servers.
   5. `Clear Logs:` This option clears all log files in the 'logs' directory. Recommended before each new registration/autio-miner-launcher run.
   6. `Exit:` This option exits the main menu and the program.

## Hotkey Naming Structure and other requirements

For the "registration_sniper" system to function correctly, it's essential to adhere to a specific naming structure for hotkeys. The naming convention is as follows:

- Hotkeys should be named in the format: `s<netuid>_<number>`, where:
  - `<netuid>` represents the Bittensor network UID (e.g., 18 for subnet18).
  - `<number>` is a sequential identifier for different hotkeys within the same subnet.

Example hotkey names: `s8_1`, `s8_2`, `s19_1`, etc.

This naming structure is crucial for the system to correctly identify and manage different hotkeys, especially when launching and monitoring miner processes.

- SSH key setup: SSH keys must be previously configured so that connections can be made without a password. [click here](docs/ssh_key_setup.md) for setup instructions.
