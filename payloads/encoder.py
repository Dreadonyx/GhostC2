import base64


def encode_base64(payload, language="python"):
    """Wrap payload in base64 one-liner for given language."""
    encoded = base64.b64encode(payload.encode()).decode()

    if language == "python":
        return f'python3 -c "exec(__import__(\'base64\').b64decode(\'{encoded}\').decode())"'
    elif language == "bash":
        return f'echo {encoded} | base64 -d | bash'
    elif language == "powershell":
        # PowerShell uses UTF-16LE
        utf16 = payload.encode("utf-16-le")
        ps_encoded = base64.b64encode(utf16).decode()
        return f'powershell -EncodedCommand {ps_encoded}'
    else:
        return f'echo {encoded} | base64 -d | sh'


def encode_xor(payload, key=0x41):
    """XOR encode payload bytes and produce Python decoder stub."""
    encoded = bytes([b ^ key for b in payload.encode()])
    hex_encoded = "".join(f"\\x{b:02x}" for b in encoded)
    stub = (
        f'python3 -c "'
        f'k={key}; p=b"{hex_encoded}"; '
        f'exec(bytes([b^k for b in p]).decode())"'
    )
    return stub


def encode_none(payload, **kwargs):
    """No encoding — return raw payload."""
    return payload


ENCODERS = {
    "none": encode_none,
    "base64": encode_base64,
    "xor": encode_xor,
}
