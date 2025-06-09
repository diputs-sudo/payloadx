# pbx/cli/config.py

VERSION = "0.0.3"

# Profile definitions per payload_type
PAYLOAD_PROFILE = {
    "reverse_shell": {
        "required": ["ip", "port", "platform", "language"],
        "optional": ["persistence", "encryption", "polymorphism", "watermark", "callback_delay", "build_mode", "output_path"],
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
        "optional": ["persistence", "polymorphism", "execute_after_download", "callback_delay", "build_mode", "output_path"],
        "defaults": {
            "persistence": "none",
            "polymorphism": "none",
            "execute_after_download": "true",
            "callback_delay": "0",
            "build_mode": "debug",
            "output_path": "./output/",
        },
    },
}

OPTIONS_INFO = {
    "platform": {
        "description": "Target operating system for the payload.",
        "allowed_values": {
            "macos": "Apple macOS operating system.",
            "linux": "Linux-based operating system.",
            "windows": "Microsoft Windows operating system.",
        },
    },
    "language": {
        "description": "Source programming language for the payload.",
        "allowed_values": {
            "python": "Python language.",
            "c": "C language.",
            "go": "Go language.",
        },
    },
    "ip": {
        "description": "Listener IP address for reverse connection.",
        "allowed_values": None,  # Free-text
    },
    "port": {
        "description": "Listener port for reverse connection.",
        "allowed_values": None,  # Free-text
    },
    "persistence": {
        "description": "Persistence mechanism on the target system.",
        "allowed_values": {
            "none": "No persistence.",
            "mac_launch_agent": "Persistence via macOS Launch Agent.",
        },
    },
    "encryption": {
        "description": "Encryption technique to apply.",
        "allowed_values": {
            "none": "No encryption.",
            "xor": "Simple XOR encryption.",
            "aes": "AES encryption.",
        },
    },
    "polymorphism": {
        "description": "Polymorphic techniques to evade static detection.",
        "allowed_values": {
            "none": "No polymorphism.",
            "basic": "Basic polymorphism.",
        },
    },
    "watermark": {
        "description": "Watermark to embed in the payload.",
        "allowed_values": None,
    },
    "callback_delay": {
        "description": "Delay between callbacks/beacons in seconds.",
        "allowed_values": None,
    },
    "build_mode": {
        "description": "Build mode for payload.",
        "allowed_values": {
            "debug": "Debug mode.",
            "release": "Release mode.",
            "dry-run": "Dry-run mode.",
        },
    },
    "output_path": {
        "description": "Directory path to save the payload.",
        "allowed_values": None,
    },
    "download_url": {
        "description": "URL to download payload from (downloader type).",
        "allowed_values": None,
    },
    "execute_after_download": {
        "description": "Whether to execute payload after download.",
        "allowed_values": {
            "true": "Execute after download.",
            "false": "Do not execute after download.",
        },
    },
}

# Help text for built-in CLI commands
BUILTIN_CMDS = {
    "list": "Show required/optional config for current payload_type.",
    "set": "Set one or more options. Format: set OPTION VALUE[, OPTION VALUE]",
    "reset": "Clear all current values and start fresh.",
    "clear": "Clear the terminal screen.",
    "build": "Build payload from the current configuration.",
    "scan": "Scan building blocks or plugins.",
    "config": "Save/load CLI configs. Usage: config save NAME | config load NAME",
    "wizard": "Start guided build wizard (planned).",
    "history": "Manage build history. Usage: history [all|find|show|on|off|clear]",
    "version": "Show current PayloadBuilder X version.",
    "help": "Show help for commands or options.",
    "exit": "Exit the shell.",
    "quit": "Alias for exit.",
}

SUBCOMMANDS = {
    "history": ["all", "find", "show", "on", "off", "clear"],
    "config": ["save", "load"],
    "scan": ["block", "plugin"],
    "help": [],
}
