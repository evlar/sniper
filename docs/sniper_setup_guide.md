
# Comprehensive Guide for PM2 Command Template, Environment variable, and SSH Server Configuration

## Introduction
This guide covers the use of the initial setup of the Sniper program and PM2 processes management, focusing on setting up environment variables, inputting server details, and understanding program limitations.

## Part 1: Automated PM2 Miner Launch Process and Environment Variable Configuration
### Once setup, the system automatically starts PM2 processes using the saved templates.

### Setup Procedure: Launch the Main Menu
Start the application by running:
```
python3 run.py
```
This opens the main menu of the application.

From the main menu, choose "PM2 Launch Command and Environment Variable Configuration" and follow the prompts for each subnet. Inputs include:
- Full path to `miner.py` for the subnet.
- API keys and other environment variables.
- Additional miner configuration parameters. (E.g. --subtensor.chain_endpoint)

## Part 2: Inputting Server Details for Launching Miners Via SSH

### From the Main Menu
From the main menu, choose "Server Details Configuration" and follow the prompts for each remote server. Inputs include:
- subnet number (e.g., 22)
- server name: (e.g., sn22 server 2)
- IP address of your server: (e.g., 12.34.56.789)
- SSH username: (e.g., root)
- SSH private key (e.g., ~/.ssh/id_ed25519_vps) [click here](https://github.com/evlar/BT_Help/blob/main/docs/ssh_key_setup.md) for SSH private key setup. 

## Limitations of the Registration Sniper Program
- **Single Server per Subnet**: Can't launch miners to multiple servers for the same subnet simultaneously.
- **User Prompt for Server Selection**: Users must select the server for subnets associated with multiple servers.
- **Manual Server Selection**: No automatic distribution of miners across multiple servers.

## Usage Rules
- **Unique Server-Subnet Association**: Each subnet number should be uniquely associated with one server name.
- **Consistent Input**: Ensure accurate server details for smooth operation.

## Conclusion
This guide provides an integrated approach to managing PM2 processes and using the Registration Sniper program. By following these steps and guidelines, users can efficiently manage environment variables and server details, streamlining the process of starting miners with the correct configurations.

## Recommendation (optional): Using `direnv` on Remote Servers
- **Project-Specific Environments**: Manage environment variables per project.
- **Security**: Environment variables are not exposed in process listings.
- **Convenience**: Automatically loads the correct environment in the project directory.
- **Setting Up `direnv`**: Instructions found [here](https://github.com/evlar/BT_Help/blob/main/docs/direnv_setup.md).

While the script's current method of setting environment variables is functional, using `direnv` provides a more robust solution for managing environment variables on remote servers.