# pbx/builder/utils.py

from pathlib import Path 
import re 

def validate_config(cfg):
    errors = []

    if "port" in cfg:
        try:
            port = int(cfg["port"])
            if not (1 <= port <= 65535):
                errors.append("port must be between 1 and 65535.")
        except ValueError:
            errors.append("port must be a valid integer.")

    if "ip" in cfg:
        host = cfg["ip"]
        ipv4 = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        ipv6 = re.compile(r"^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$")
        if not (ipv4.match(host) or ipv6.match(host)):
            errors.append("ip must be a valid IPv4 or IPv6 address.")
        
        return errors 
    
def get_extension_for_language(lang):
    lang = lang.lower()
    mapping = {
        "python": "py",
        "c": "c",
        "cpp": "cpp",
        "go": "go",
        "bash": "sh",
        "powershell": "ps1",
        "javascript": "js",
        "ruby": "rb",
        "perl": "pl"
    }
    return mapping.get(lang, "txt") # fall back for unknown language

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)