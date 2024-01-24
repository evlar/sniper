# User Guide for Registration Sniper Program

## Introduction
This guide provides instructions on how to use the Registration Sniper program, specifically focusing on inputting server details and understanding the program's limitations.

## Inputting Server Details
To input server details into the program, follow these steps:

1. **Access the Main Menu**: Run the program to access the main menu.
2. **Select Option 2**: From the main menu, select option 2, which is for saving SSH key paths for remote miner launching.
3. **Enter Subnet Number**: When prompted, enter the subnet number (e.g., '18' for subnet18).
4. **Enter Server Name**: Input the server name that you wish to associate with the subnet number.
5. **Enter IP Address**: Provide the IP address of the VPS (Virtual Private Server) you are using.
6. **Enter SSH Username**: Input the SSH username for the server.
7. **Enter SSH Key Path**: Provide the path to the SSH private key (e.g., `~/.ssh/id_ed25519_vps`).

The program will save these details and use them to launch miners remotely.

## Limitations of the Program
The Registration Sniper program has the following limitations:

- **Single Server per Subnet**: The program is designed to launch miners to only one server per subnet at a time. It cannot handle launching miners to multiple servers for the same subnet simultaneously.
- **User Prompt for Server Selection**: If a subnet is associated with more than one server, the program will prompt the user to select the server they wish to use. It is essential to ensure that each subnet number is associated with a unique server name before launching miners.
- **Manual Server Selection**: Users must manually select the server when prompted if multiple servers are available for a subnet. The program does not automatically balance or distribute miners across multiple servers.

## Usage Rules
When using the program, please adhere to the following rules:

- **Unique Server-Subnet Association**: Ensure that each subnet number is associated with only one server name at any given time. This is crucial for the correct operation of the program.
- **Consistent Input**: Provide consistent and accurate server details when prompted to avoid any issues with launching miners.

By following these guidelines and understanding the program's limitations, users can effectively manage and launch miners using the Registration Sniper program.