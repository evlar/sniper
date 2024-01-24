
# SSH Key Setup Instructions Using id_ed25519

## 1. Generate the SSH Key Pair on the Client Machine
- Open the terminal on the client machine (the machine that will connect to the Ubuntu server).
- Run `ssh-keygen -t ed25519` to generate a new SSH key pair using the Ed25519 algorithm.
- When prompted, enter a file in which to save the key. Press Enter to accept the default location (`~/.ssh/id_ed25519`).
- Optionally, enter a passphrase for additional security or press Enter for no passphrase.

## 2. Copy the Public Key to the Ubuntu Server
- Use the command `ssh-copy-id username@server-ip-address` to copy the public key to the Ubuntu server.
- Replace `username` with your actual username on the server and `server-ip-address` with the server's actual IP address or hostname.
- Enter your password when prompted. This will be the last time you'll need to enter the password for SSH connections.

## 3. Login to the Server to Confirm
- Now, try logging in to the server using SSH: `ssh username@server-ip-address`.
- If everything is set up correctly, you should be logged in without being asked for a password.

## 4. Disable Password Authentication
- For enhanced security, consider disabling password authentication on the server.
- On the server, edit the SSH config file: `sudo nano /etc/ssh/sshd_config`.
- Find the line `#PasswordAuthentication yes` and change it to `PasswordAuthentication no`.
- Save the file and restart the SSH service: `sudo systemctl restart sshd`.

## 5. Troubleshooting
- If you're unable to log in without a password, check the permissions of the `.ssh` directory and the `authorized_keys` file on the server. They should be owned by your user. Set the permissions with: `chmod 700 ~/.ssh` and `chmod 600 ~/.ssh/authorized_keys`.

> Note: These steps assume SSH is installed and running on both the client and the Ubuntu server. Be cautious when disabling password authentication, as it prevents password-based logins from any client that doesn't have the corresponding private key.