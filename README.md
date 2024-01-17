# README.md for registration_sniper

## Project Overview

"registration_sniper" is a Python-based tool designed for the Bittensor network. It automates the process of registering neurons when the fee falls below a threshold, launches miners automatically, and manages subtensor endpoints and wallet configurations. The project is structured with a clear separation of concerns, making it easy to maintain and extend.

## Features

- **Registration Sniper**: Monitors registration fees and registers neurons when the fee is affordable.
- **Auto Miner Launcher**: Automates the launching of miners for different hotkeys and subnets, both locally and remotely.
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

## Usage

1. **Run the Application**:
   ```
   python3 run.py
   ```
   This will launch the main menu, providing options to manage registration snipers and auto miner launchers.

2. **Main Menu Options**:
   - Registration Sniper: Manage registration processes based on current fee thresholds.
   - Auto Miner Launcher (Local): Start miners automatically for registered hotkeys on the local machine.
   - Auto Miner Launcher (Remote): Launch miner processes on remote machines for registered hotkeys.
   - Save PM2 Command Templates: Configure PM2 command templates for different subnets.

## Remote Miner Launcher

The remote miner launcher feature extends the auto miner launcher functionality by enabling the starting of miner processes on remote servers. This is useful when managing a fleet of miners distributed across different machines.

To use this feature:

- Configure SSH details for the remote servers in `data/ssh_details.json`.
- Use the main menu to launch miners remotely, specifying the desired subtensor endpoint.
- The system will handle the process of connecting to the remote server, validating the registration status of hotkeys, and initiating the miner processes.

## Hotkey Naming Structure

For the "registration_sniper" system to function correctly, it's essential to adhere to a specific naming structure for hotkeys. The naming convention is as follows:

- Hotkeys should be named in the format: `s<netuid>_<number>`, where:
  - `<netuid>` represents the Bittensor network UID (e.g., 18 for subnet18).
  - `<number>` is a sequential identifier for different hotkeys within the same subnet.

Example hotkey names: `s8_1`, `s8_2`, `s19_1`, etc.

This naming structure is crucial for the system to correctly identify and manage different hotkeys, especially when launching and monitoring miner processes.

## Project Structure

- `src/`: Contains the core Python modules.
- `data/`: Stores JSON configuration files like subtensor endpoints, miner PM2 templates, and SSH details for remote servers.
- `logs/`: Log files for different processes.
- `run.py`: Entry point for running the main menu.
- `requirements.txt`: Lists the Python dependencies.

## Contributing

Contributions to "registration_sniper" are welcome. Please adhere to the following guidelines:

1. Fork the repository and create your branch from `main`.
2. Write clear and concise commit messages.
3. Ensure your code adheres to the project's style and requirements.
4. Create a pull request.

For any substantial changes, please open an issue first to discuss what you would like to change.

## License

Please make sure to update the license as appropriate for your project.