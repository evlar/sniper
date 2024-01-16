# main_menu.py
import subprocess
import os
import json
from getpass import getpass
from miner_launcher import auto_miner_launcher

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
    subnet = input("Enter the subnet number (e.g., '18' for subnet18): ")
    path_to_miner = input("Enter the path to the miner.py for this subnet: ")
    logging_debug = input("Is logging.debug enabled for this subnet? (yes/no): ").lower() == 'yes'

    # Prompt for additional parameters
    additional_params = {}
    while True:
        param_name = input("Enter additional parameter name (or 'done' to finish): ")
        if param_name.lower() == 'done':
            break
        param_value = input(f"Enter value for {param_name}: ")
        additional_params[param_name] = param_value

    # Save the template with additional parameters
    templates = read_templates()
    templates[f"subnet{subnet}"] = {
        "path_to_miner": path_to_miner,
        "logging_debug": logging_debug,
        "additional_params": additional_params
    }
    save_templates(templates)


def start_auto_miner_launcher():
    bt_endpoint = choose_subtensor_endpoint()  # Get the subtensor endpoint
    launcher_script_path = os.path.join(os.path.dirname(__file__), '..', 'launch_auto_miner.py')
    subprocess.run(['pm2', 'start', launcher_script_path, '--interpreter', 'python3', '--name', 'auto_miner_launcher', '--', '--endpoint', bt_endpoint])
    print("Auto Miner Launcher started as PM2 process.")


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Registration Sniper")
        print("2. Auto Miner Launcher")
        print("3. Save PM2 Launch Command Templates for Each Subnet")
        print("4. Exit")

        choice = input("Enter the number of your choice: ")

        if choice == '1':
            registration_sniper()
        elif choice == '2':
            start_auto_miner_launcher()
        elif choice == '3':
            save_pm2_command_template()
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

# Run the main menu
if __name__ == "__main__":
    main_menu()

