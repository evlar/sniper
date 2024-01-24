
# PM2 Processes Start Command and Environment Variable Configuration through the Sniper Main Menu:

To configure environment variables for PM2 processes through the main menu, follow the instructions below:

## Step 1: Launch the Main Menu

Start the application by running the following command in your terminal:

bash
python3 run.py


This command will open the main menu of the application.

## Step 2: Save PM2 Command Templates

From the main menu, choose the option to "Save PM2 Command Templates" for each subnet you intend to work with. This will involve the following inputs:

- The full path to the `miner.py` for the subnet.
- Names and values for API keys as environment variables.
- Any additional parameters that your miner configuration requires.

The system will prompt you for these details and save them as templates for later use.

## Step 3: Start the Auto Miner Launcher

When you're ready to start mining, select either "Auto Miner Launcher (locally)" or "Auto Miner Launcher (remotely)" from the main menu. This decision depends on whether you want to start the miner processes on your local machine or on a remote server.

- For local launching, the system will use the saved PM2 command templates to start the miner processes with the necessary environment variables on your local machine.
- For remote launching, the system will additionally handle the SSH connection to the remote server and start the miner processes there using the saved templates.

## Step 4: Automated PM2 Process Handling

The system will automatically handle the starting of the PM2 process with the environment variables set according to the saved templates. There's no need for manual input each time you start a miner.

By following these steps, you can efficiently manage the environment variables for PM2 processes directly from the main menu, streamlining the process of starting miners with the correct configurations.

### How It Works

1. **Extract Environment Variables**: The script extracts environment variables from a template configuration, which includes API keys and other necessary variables.

2. **Construct Command**: These variables are then concatenated into a string that forms the initial part of the command to start the PM2 process.

3. **Execute Command**: When the command is executed, either locally or via SSH for remote processes, the environment variables are set for the scope of the PM2 process being started.


## Recommendation: Using `direnv` on Remote Servers

While the current script handles environment variables within the PM2 command, it's recommended to manage environment variables on the remote server using `direnv`. This tool allows you to load and unload environment variables depending on the current directory, which is particularly useful for managing different projects with different configurations.

### Setting Up `direnv`

Instructions for setting up `direnv` found here: https://github.com/evlar/BT_Help/blob/main/docs/direnv_setup.md


### Benefits of `direnv`

- **Project-Specific Environments**: Each project can have its own set of environment variables, reducing the risk of conflicts.
- **Security**: Environment variables are not exposed in process listings.
- **Convenience**: Automatically loads the correct environment when you enter the project directory.

### Conclusion

While the script's current method of setting environment variables is functional, using `direnv` provides a more robust and flexible solution for managing environment variables, especially for manual operations on the remote server. It's a recommended addition to your workflow for better environment variable management.