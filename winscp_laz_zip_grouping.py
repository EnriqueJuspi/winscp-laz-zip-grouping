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

# Get raw directory listing from root path + /LAS subfolder
def get_file_listing(config):
    remote = config["remote_path"]
    commands = f"""
        open sftp://{config['username']}:{config['password']}@{config['host']}
        cd "{remote}"
        ls
        ls LAS
        exit
    """
    return execute_winscp(commands)

# Parse WinSCP ls output and extract filenames only
def parse_ls_output(output):
    files = []

    for line in output.splitlines():
        line = line.strip()

        # skip empty lines and WinSCP headers
        if not line or line.lower().startswith(("listing", "total")):
            continue

        parts = line.split()
        if len(parts) < 8:
            continue

        filename = " ".join(parts[7:])
        files.append(filename)
    return files

# Split file list into .zip and .laz groups
def split_files(files):
    zip_files = []
    laz_files = []

    for f in files:
        if f.endswith(".zip"):
            zip_files.append(f)
        elif f.endswith(".laz"):
            laz_files.append(f)

    return zip_files, laz_files

# Index files by filename without extension for matching
def index_folder(files):
    index = {}

    for f in files:
        if f.endswith(".zip"):
            key = f.rsplit(".", 1)[0]
        elif f.endswith(".laz"):
            key = f.rsplit(".", 1)[0]
        else:
            continue

        index[key] = f


    return index
# Match .zip and .laz files by shared filename key
def match_files(folder_a, folder_b):
    index_a = index_folder(folder_a)
    index_b = index_folder(folder_b)

    common = set(index_a) & set(index_b)

    pairs = [(index_a[k], index_b[k]) for k in sorted(common)]
    only_a = [index_a[k] for k in sorted(set(index_a) - common)]
    only_b = [index_b[k] for k in sorted(set(index_b) - common)]

    return pairs, only_a, only_b

# Entry point
def main():
    config = load_config()
    print("=" * 50)
    print("STEP 1 - GET FILE LIST")
    print(f"Path : {config['remote_path']}")
    print("=" * 50)
 
    output = get_file_listing(config)

    files = parse_ls_output(output)
    zip_files, laz_files = split_files(files)
    
    pairs, only_zip, only_laz = match_files(zip_files, laz_files)
    
    print("PAIRS:")
    for z, l in pairs:
        print(z, "<->", l)
    
    print("\nONLY ZIP:", only_zip)
    print("ONLY LAZ:", only_laz)
    
if __name__ == "__main__":
    main()