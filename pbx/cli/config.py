# pbx/cli/config.py

OPTIONS = {
    "payload_type": ["reverse_shell", "keylogger", "dropper"],
    "language": ["python"],
    "platform": ["macos"],
    "LHOST": None,
    "LPORT": None,
    "callback_delay": None,
    "stealth": ["none", "xor", "obfuscate_vars"],
    "persistence": ["none", "mac_launch_agent"],
    "output_path": None,
    "filename": None,
    "variant": ["short", "medium", "long", "ultra"],
    "build_mode": ["debug", "release", "dry-run"],
}

DESCR = {
    "payload_type": "Kind of payload to generate (reverse shell, dropper, …).",
    "language": "Source language for the generated payload.",
    "platform": "Target operating system (macOS in MVP).",
    "LHOST": "Listener IP for reverse connections.",
    "LPORT": "Listener port.",
    "callback_delay": "Delay (s) between callbacks/beacons.",
    "stealth": "Obfuscation layers to apply.",
    "persistence": "Persistence mechanism on target.",
    "output_path": "Folder for generated payload (default ./output/).",
    "filename": "Output filename (no extension).",
    "variant": "Length/Functions of the payload (short, medium, long, ultra).",
    "build_mode": "debug / release / dry-run.",
}

BUILTIN_CMDS = {
    "list": "Show current configuration and which values are required.",
    "set": "Set one or more options. Format: set OPTION VALUE[, OPTION VALUE]",
    "reset": "Clear all current values and start fresh.",
    "clear": "Clear the terminal screen.",
    "build": "Build payload from the current configuration.",
    "help": "Show help for commands or options.",
    "exit": "Exit the shell.",
    "quit": "Alias for exit."
}

DEFAULTS = {
    "output_path": "./output/",
    "callback_delay": "0",
    "stealth": "none",
    "persistence": "none",
    "build_mode": "debug",
}

PAYLOAD_REQS = {
    "reverse_shell": ["LHOST", "LPORT"],
    "keylogger": [],
    "dropper": ["persistence", "filename"],
}

BASE_REQ_NO = ["payload_type"]
BASE_REQ_WITH = ["payload_type", "language", "platform"]

CAP_MAP = {"lhost": "LHOST", "lport": "LPORT"}


PAYLOAD_PROFILE = {
    "reverse_shell": {
        "required": ["ip", "port", "platform", "language"],
        "optional": ["persistence", "encryption", "polymorphism", "watermark"],
        "defaults": {
            "persistence": "none",
            "encryption": "none",
            "polymorphism": "none",
            "watermark": "none",
            "callback_delay": "0",
            "build_mode": "debug",
            "output_path": "./output/",
        },
    },
    "downloader": {
        "required": ["platform", "language", "download_url"],
        "optional": ["persistence", "polymorphism", "execute_after_download"],
        "defaults": {
            "persistence": "none",
            "polymorphism": "none",
            "execute_after_download": "true",
            "callback_delay": "0",
            "build_mode": "debug",
            "output_path": "./output/",
        },
    },
    # more profiles
}
