import json
import subprocess

# ===== LOAD CONFIG =====
with open("sftp_config.json", "r") as f:
    config = json.load(f)

host = config["host"]
username = config["username"]
password = config["password"]
remote_path = config["remote_path"]

# ===== BUILD COMMANDS =====
commands = f"""
open sftp://{username}:{password}@{host}
cd "{remote_path}"
pwd
ls
exit
"""

print("STEP 1 - GET FILE LIST")
result = subprocess.run(
    ["winscp.com"],
    input=commands,
    capture_output=True,
    text=True
)

output = result.stdout

print(output)
