def get_full_sysinfo(session):
    """Run comprehensive sysinfo commands on session."""
    results = {}

    commands = {
        "OS":         "uname -a 2>/dev/null || ver",
        "Hostname":   "hostname",
        "User":       "whoami",
        "ID":         "id 2>/dev/null || echo N/A",
        "Shell":      "echo $SHELL",
        "CWD":        "pwd",
        "Home":       "echo $HOME",
        "Path":       "echo $PATH",
        "Network":    "ip addr 2>/dev/null || ifconfig 2>/dev/null | head -20",
        "Processes":  "ps aux 2>/dev/null | head -15",
        "Sudo":       "sudo -l 2>/dev/null || echo N/A",
        "SUID":       "find / -perm -4000 2>/dev/null | head -10",
        "Cron":       "cat /etc/crontab 2>/dev/null || echo N/A",
        "Passwd":     "cat /etc/passwd 2>/dev/null | head -10",
        "Env":        "env 2>/dev/null | head -20",
    }

    for label, cmd in commands.items():
        result = session.execute(cmd, timeout=8)
        results[label] = result or "N/A"

    return results


def print_sysinfo(info, logger):
    """Pretty-print sysinfo results."""
    logger.section("System Information")
    for label, value in info.items():
        if value and value != "N/A":
            print(f"\n  \033[36m{label}:\033[0m")
            for line in value.split("\n")[:5]:
                print(f"    {line}")
