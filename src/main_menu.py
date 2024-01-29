# main_menu.py
import subprocess
import shutil
import os
import json
from getpass import getpass
from miner_launcher import read_sniper_log
#from miner_launcher_remote import start_auto_miner_launcher_remote


def log_sniper_process(pm2_name, sniper_details):
    # Path one level up from the current script directory
    script_dir = os.path.dirname(os.path.dirname(__file__))

    # Set the path for the log file
    log_file_path = os.path.join(script_dir, 'logs', 'sniper_processes.log')

    os.makedirs(os.path.join(script_dir, 'logs'), exist_ok=True)

    # Add an initial status to the sniper details
    sniper_details['status'] = 'active'

    with open(log_file_path, 'a') as log_file:
        json_data = json.dumps(sniper_details)
        log_file.write(f"{pm2_name}: {json_data}\n")

def read_endpoints():
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')  # Adjusted path
    endpoints_file = 'subtensor_endpoints.json'
    endpoints_path = os.path.join(data_folder, endpoints_file)
    
    if os.path.exists(endpoints_path):
        with open(endpoints_path, 'r') as file:
            return json.load(file)
    else:
        return []

def save_endpoint(endpoint):
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')  # Adjusted path
    endpoints_file = 'subtensor_endpoints.json'
    endpoints_path = os.path.join(data_folder, endpoints_file)

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    endpoints = read_endpoints()
    endpoints.append(endpoint)
    with open(endpoints_path, 'w') as file:
        json.dump(endpoints, file)

def choose_subtensor_endpoint():
    subtensor_choice = input("Local or Remote subtensor? (local/remote): ").lower()
    if subtensor_choice == "remote":
        endpoints = read_endpoints()
        if endpoints:
            print("Saved endpoints:")
            for i, endpoint in enumerate(endpoints, start=1):
                print(f"{i}. {endpoint}")
            print("Choose from selection or enter manually:")
            endpoint_choice = input("Enter your choice: ")

            if endpoint_choice.isdigit() and int(endpoint_choice) <= len(endpoints):
                return endpoints[int(endpoint_choice) - 1]
            else:
                bt_endpoint = endpoint_choice
                save_choice = input("Would you like to save this new endpoint for later use? (yes/no): ")
                if save_choice.lower() == 'yes':
                    save_endpoint(bt_endpoint)
                return bt_endpoint
        else:
            print("Enter subtensor endpoint:")
            bt_endpoint = input("Enter your Bittensor endpoint: ")
            save_choice = input("Would you like to save this new endpoint for later use? (yes/no): ")
            if save_choice.lower() == 'yes':
                save_endpoint(bt_endpoint)
            return bt_endpoint
    else:
        return "ws://127.0.0.1:9944"
    

def registration_sniper():
    bt_netuid = input("To which subnet would you like to register?: ")
    registration_fee_threshold = input("Enter the registration fee threshold: ")
    bt_endpoint = choose_subtensor_endpoint()  # Use the extracted function for endpoint selection

    # Determine if the chosen endpoint is remote or local
    subtensor_choice = "remote" if bt_endpoint.startswith("ws://") else "local"

    wallets_path = os.path.expanduser('~/.bittensor/wallets/')
    
    try:
        wallet_names = os.listdir(wallets_path)
    except FileNotFoundError:
        print("The wallet directory does not exist.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    
    if not wallet_names:
        print("No wallets found in the directory.")
        return
    
    print("Available wallets:")
    for index, wallet_name in enumerate(wallet_names, start=1):
        print(f"{index}. {wallet_name}")
    
    wallet_index = input("Which wallet would you like to use? (Enter number): ")
    try:
        selected_wallet = wallet_names[int(wallet_index) - 1]
    except (ValueError, IndexError):
        print("Invalid selection. Please enter a number corresponding to the wallet.")
        return

    hotkeys_path = os.path.join(wallets_path, selected_wallet, 'hotkeys')
    
    try:
        all_hotkey_names = os.listdir(hotkeys_path)
    except FileNotFoundError:
        print(f"The hotkeys directory for wallet '{selected_wallet}' does not exist.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    subnet_prefix = f"s{bt_netuid}_"
    hotkey_names = [hk for hk in all_hotkey_names if hk.startswith(subnet_prefix)]

    # Sort the hotkeys by the numerical part
    hotkey_names.sort(key=lambda x: int(x.split('_')[1]))

    if not hotkey_names:
        print(f"No hotkeys found for subnet '{bt_netuid}' in the wallet '{selected_wallet}'.")
        return

    print(f"Available hotkeys for subnet '{bt_netuid}' in wallet '{selected_wallet}':")
    for index, hotkey_name in enumerate(hotkey_names, start=1):
        print(f"{index}. {hotkey_name}")
    
    print("Enter hotkey numbers to register (comma-separated, e.g., 1,3,4):")
    hotkey_indices = input().split(',')
    selected_hotkeys = []
    for index in hotkey_indices:
        try:
            selected_hotkey = hotkey_names[int(index.strip()) - 1]
            selected_hotkeys.append(selected_hotkey)
        except (ValueError, IndexError):
            print(f"Invalid selection: {index}. Skipping.")

    if not selected_hotkeys:
        print("No valid hotkeys selected.")
        return

    bt_cold_pw_wallet = getpass("Enter your Bittensor wallet password: ")

    for selected_hotkey in selected_hotkeys:
        sniper_script_path = os.path.join(os.path.dirname(__file__), 'registration_sniper.py')
        pm2_name = f"sniper_{selected_hotkey}"

        # Construct the command with the correct subtensor choice
        command = [
            'pm2', 'start', sniper_script_path,
            '--interpreter', 'python3',  # Specifying the interpreter
            '--name', pm2_name,
            '--',
            '--wallet-name', selected_wallet,
            '--hotkey-name', selected_hotkey,
            '--wallet-password', bt_cold_pw_wallet,
            '--subtensor', subtensor_choice,  # Using the correct subtensor choice
            '--endpoint', bt_endpoint,
            '--netuid', bt_netuid,
            '--threshold', registration_fee_threshold,
        ]

        subprocess.run(command)
        print(f"Launched {selected_hotkey} in pm2 instance named {pm2_name}.")

        # Log the sniper process
        sniper_details = {
            'wallet_name': selected_wallet,
            'hotkey_name': selected_hotkey,
            'subtensor_choice': subtensor_choice,
            'endpoint': bt_endpoint,
            'netuid': bt_netuid,
            'threshold': registration_fee_threshold
        }
        log_sniper_process(pm2_name, sniper_details)

#######################################################################################################################################################

def save_templates(templates):
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    templates_file = 'miner_pm2_template.json'
    templates_path = os.path.join(data_folder, templates_file)

    with open(templates_path, 'w') as file:
        json.dump(templates, file, indent=4)

def read_templates():
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    templates_file = 'miner_pm2_template.json'
    templates_path = os.path.join(data_folder, templates_file)

    if os.path.exists(templates_path):
        with open(templates_path, 'r') as file:
            return json.load(file)
    return {}



def save_pm2_command_template():
    subnet = input("Enter the subnet number: ")
    path_to_miner = input("Enter the full path to the miner.py for this subnet: ")
    
    # Prompt for API keys
    api_keys = {}
    while True:
        api_key_name = input("Enter the environment variable name for the API key (or 'done' to finish API keys): ")
        if api_key_name.lower() == 'done':
            break
        api_key_value = input(f"Enter the API key for {api_key_name}: ")
        api_keys[api_key_name] = api_key_value

    # Prompt for additional parameters
    additional_params = {}
    while True:
        param_name = input("Enter additional parameter name (or 'done' to finish additional parameters): ")
        if param_name.lower() == 'done':
            break
        param_value = input(f"Enter value for {param_name}: ")
        additional_params[param_name] = param_value

    logging_debug = input("Is logging.debug enabled for this subnet? (yes/no): ").lower() == 'yes'

    # Save the template with path, API keys, additional parameters, and logging option
    templates = read_templates()
    templates[f"subnet{subnet}"] = {
        "path_to_miner": path_to_miner,
        "api_keys": api_keys,
        "additional_params": additional_params,
        "logging_debug": logging_debug
    }
    save_templates(templates)


def start_auto_miner_launcher():
    bt_endpoint = choose_subtensor_endpoint()  # Get the subtensor endpoint
    launcher_script_path = os.path.join(os.path.dirname(__file__), '..', 'launch_auto_miner.py')
    subprocess.run(['pm2', 'start', launcher_script_path, '--interpreter', 'python3', '--name', 'auto_miner_launcher', '--', '--endpoint', bt_endpoint])
    print("Auto Miner Launcher started as PM2 process.")

def start_auto_miner_launcher_remote():
    bt_endpoint = choose_subtensor_endpoint()  # Get the subtensor endpoint
    ssh_details = read_ssh_details()
    sniper_processes = read_sniper_log()
    active_subnets = {details['netuid'] for _, details in sniper_processes if details['status'] == 'active' and details['endpoint'] == bt_endpoint}

    server_selections = {}
    for subnet in active_subnets:
        servers = ssh_details.get(f"subnet{subnet}", [])
        if len(servers) > 1:
            print(f"Multiple servers found for subnet {subnet}:")
            for i, server in enumerate(servers, start=1):
                print(f"{i}. {server['server_name']}")
            server_choice = input("Select the server number to use: ")
            try:
                selected_server = servers[int(server_choice) - 1]['server_name']
                server_selections[subnet] = selected_server
            except (ValueError, IndexError):
                print(f"Invalid selection. Please enter a number between 1 and {len(servers)}.")
                return
        elif len(servers) == 1:
            server_selections[subnet] = servers[0]['server_name']
        else:
            print(f"No servers found for subnet {subnet}.")
            return

    for subnet, server_name in server_selections.items():
        # Now that we have the selected server, we can start the remote miner launcher
        launcher_script_path = os.path.join(os.path.dirname(__file__), '..', 'launch_auto_miner_remote.py')
        subprocess.run([
            'pm2', 'start', launcher_script_path, '--interpreter', 'python3',
            '--name', f"auto_miner_launcher_remote_{subnet}", '--',
            '--endpoint', bt_endpoint, '--server-name', server_name
        ])
        print(f"Remote Auto Miner Launcher started for server {server_name} on subnet {subnet} as PM2 process.")

def clear_all_logs():
    script_dir = os.path.dirname(os.path.dirname(__file__))
    logs_dir = os.path.join(script_dir, 'logs')

    for filename in os.listdir(logs_dir):
        if filename == '.gitkeep':  # Skip .gitkeep file
            continue

        file_path = os.path.join(logs_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"Deleted: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {file_path}")
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def save_ssh_details():
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    ssh_details_file = 'ssh_details.json'
    ssh_details_path = os.path.join(data_folder, ssh_details_file)

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    if os.path.exists(ssh_details_path):
        with open(ssh_details_path, 'r') as file:
            ssh_details = json.load(file)
    else:
        ssh_details = {}

    subnet = input("Enter the subnet number (e.g., '18' for subnet18): ")
    server_name = input("Enter the server name: ")
    ip_address = input("Enter the IP address of the VPS: ")
    username = input("Enter the SSH username: ")
    key_path = input("Enter the path to the SSH private key (e.g., ~/.ssh/id_ed25519_vps): ")

    ssh_details.setdefault(f"subnet{subnet}", []).append({
        "server_name": server_name,
        "ip_address": ip_address,
        "username": username,
        "key_path": key_path
    })

    with open(ssh_details_path, 'w') as file:
        json.dump(ssh_details, file, indent=4)

    print(f"SSH details saved for server {server_name} on subnet {subnet}.")

def read_ssh_details():
    with open('data/ssh_details.json', 'r') as file:
        return json.load(file)

def open_axon_ports():
    script_path = os.path.join(os.path.dirname(__file__), 'open_axon_ports.py')
    subprocess.run(['python3', script_path])
    print("open_axon_ports.py has been executed.")

def main_menu():
    while True:
        print("\n\033[1mWelcome to the Registration Sniper\033[0m")
        print("\033[93mNote: Hotkeys must be named in the format: `s<netuid>_<number>`\033[0m")
        print("\033[93mExample: s8_1, s8_2, s8_3, etc.\033[0m")
        print("\033[93mNote: Ensure consitant wallet.name across all machines\033[0m")
        print("\nMain Menu:")
        print("1. PM2 Launch Command and Environment Variable Configuration:")
        print("2. Server Details Configuration")
        print("\033[92m3. Registration Sniper \033[93m Run for each subnet you plan to register on prior to running Auto Miner\033[0m")
       # print("4. Auto Miner Launcher (locally) \033[91m Not working on a Contabo VPS\033[0m")

        print("\033[92m4. Auto Miner Launcher (remotely) \033[0m \033[93m Launches miners on relevant remote VPS provided that your SSH key path has been set\033[0m")
        print("5. Clear Logs")
        #print("6. Open Axon Ports with PM2")
        print("6. Exit")

        choice = input("Enter the number of your choice: ")

        if choice == '1':
            save_pm2_command_template()
        elif choice == '2':
            save_ssh_details()
        elif choice == '3':
            registration_sniper()
       # elif choice == '4':
        #    start_auto_miner_launcher()
        elif choice == '4':
            start_auto_miner_launcher_remote()
        elif choice == '5':
            print("\033[91mWARNING: Clearing logs will delete all log files in the 'logs' directory.\033[0m")
            print("This may include important information about ongoing or past processes.")
            print("Proceed only if you are sure that you don't need these logs.")
            confirm = input("Type 'yes' to confirm log deletion: ").lower()
            if confirm == 'yes':
                print("Clearing logs...")
                clear_all_logs()
            else:
                print("Log deletion cancelled.")
       # elif choice == "6":
           # open_axon_ports()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")

# Run the main menu
if __name__ == "__main__":
    main_menu()


