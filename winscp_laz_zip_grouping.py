import json
import subprocess

# Load SFTP configuration from JSON file
def load_config(config_file="sftp_config.json"):
    with open(config_file, "r") as f:
        return json.load(f)

# Execute WinSCP command and return output
def execute_winscp(commands):
    result = subprocess.run(
        ["winscp.com"],
        input=commands,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout

# Connect to SFTP and list target folder files
def get_folder_listing(config):
    commands = f"""
open sftp://{config['username']}:{config['password']}@{config['host']}
cd "{config['remote_path']}"
pwd
ls
exit
"""

    return execute_winscp(commands)

# Entry point
def main():
    config = load_config()

    print("STEP 1 - GET FILE LIST")

    output = get_folder_listing(config)

    print(output)


if __name__ == "__main__":
    main()