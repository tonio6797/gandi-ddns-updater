import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple, TypedDict
import requests

class RRSetPayload(TypedDict, total=False):
    rrset_values: List[str]
    rrset_ttl: int

def _log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def _cache_path(filename: str) -> str:
    """Return a writable path for a cache file, falling back to the system temp dir."""
    preferred = os.path.join("/run", filename)
    try:
        os.makedirs("/run", exist_ok=True)
        # Check we can actually write there
        if os.access("/run", os.W_OK):
            return preferred
    except OSError:
        pass
    import tempfile
    return os.path.join(tempfile.gettempdir(), filename)

CACHE_KEY_IPV4 = _cache_path("ipv4.last")
CACHE_KEY_IPV6 = _cache_path("ipv6.last")

def _get_env_var(
    name: str, default: Optional[str] = None, required: bool = False
) -> Optional[str]:
    try:
        return os.environ[name]
    except KeyError:
        if required:
            raise ValueError(
                f"The {name} environment variable is required but not set."
            )
        return default

def _get_cache_value(key: str) -> Optional[str]:
    try:
        with open(key) as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def _set_cache_value(key: str, value: str) -> str:
    with open(key, "w") as f:
        f.write(value)
    return value

def _get_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if GANDI_PAT:
        headers["Authorization"] = f"Bearer {GANDI_PAT}"
    elif GANDI_API_KEY:
        headers["Authorization"] = f"Apikey {GANDI_API_KEY}"
    return headers

def notify(message: str, shoutrrr_urls: Optional[List[str]]) -> None:
    if not shoutrrr_urls:
        return
    url_args = []
    for url in shoutrrr_urls:
        url_args += ["--url", url]
    try:
        env = os.environ.copy()
        env["SHOUTRRR_URL"] = shoutrrr_urls[0]
        result = subprocess.run(
            ["shoutrrr", "send"] + url_args + ["--message", message],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.stdout:
            _log(f"Notification sent: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        _log(f"Failed to send notification: {e.stderr.strip()}")
    except FileNotFoundError:
        _log("shoutrrr binary not found, skipping notification")

def get_ipv4() -> Tuple[Optional[str], bool]:
    try:
        response = requests.get("https://ipv4.icanhazip.com/")
        response.raise_for_status()
    except Exception:
        address = None
    else:
        address = response.text.strip()
    changed = False
    if address and address != _get_cache_value(CACHE_KEY_IPV4):
        _set_cache_value(CACHE_KEY_IPV4, address)
        changed = True
    return (address, changed)

def get_ipv6() -> Tuple[Optional[str], bool]:
    try:
        response = requests.get("https://ipv6.icanhazip.com/")
        response.raise_for_status()
    except Exception:
        address = None
    else:
        address = response.text.strip()
    changed = False
    if address and address != _get_cache_value(CACHE_KEY_IPV6):
        _set_cache_value(CACHE_KEY_IPV6, address)
        changed = True
    return (address, changed)

def update_a_record() -> None:
    ip, changed = get_ipv4()
    if not ip:
        _log("Unable to fetch current IPV4 address")
    elif changed:
        try:
            payload: RRSetPayload = {"rrset_values": [ip]}
            if GANDI_TTL:
                payload["rrset_ttl"] = int(GANDI_TTL)
            response = requests.put(
                f"{GANDI_URL}{GANDI_DOMAIN}/records/{GANDI_RECORD}/A",
                json=payload,
                headers=_get_headers(),
            )
            response.raise_for_status()
        except Exception as e:
            message = f"Unable to update A record '{GANDI_RECORD}' for {GANDI_DOMAIN}: {e}"
            _log(message)
            notify(message, SHOUTRRR_URLS)
        else:
            message = f"Set IP to {ip} for A record '{GANDI_RECORD}' for {GANDI_DOMAIN}"
            _log(message)
            notify(message, SHOUTRRR_URLS)
    else:
        _log(f"No change in external IP ({ip}), not updating A record")

def update_aaaa_record() -> None:
    ip, changed = get_ipv6()
    if not ip:
        _log("Unable to fetch current IPV6 address")
    elif changed:
        try:
            payload: RRSetPayload = {"rrset_values": [ip]}
            if GANDI_TTL:
                payload["rrset_ttl"] = int(GANDI_TTL)
            response = requests.put(
                f"{GANDI_URL}{GANDI_DOMAIN}/records/{GANDI_RECORD}/AAAA",
                json=payload,
                headers=_get_headers(),
            )
            response.raise_for_status()
        except Exception as e:
            message = f"Unable to update AAAA record '{GANDI_RECORD}' for {GANDI_DOMAIN}: {e}"
            _log(message)
            notify(message, SHOUTRRR_URLS)
        else:
            message = f"Set IP to {ip} for AAAA record '{GANDI_RECORD}' for {GANDI_DOMAIN}"
            _log(message)
            notify(message, SHOUTRRR_URLS)
    else:
        _log(f"No change in external IP ({ip}), not updating AAAA record")

if __name__ == "__main__":
    GANDI_URL = _get_env_var("GANDI_URL", "https://api.gandi.net/v5/livedns/domains/")
    GANDI_PAT = _get_env_var("GANDI_PAT")
    GANDI_API_KEY = _get_env_var("GANDI_API_KEY")
    GANDI_DOMAIN = _get_env_var("GANDI_DOMAIN", required=True)
    GANDI_RECORD = _get_env_var("GANDI_RECORD", "@")
    GANDI_TTL = _get_env_var("GANDI_TTL")
    SHOUTRRR_URLS = [
        u.strip().strip('\'"').strip()
        for u in (_get_env_var("SHOUTRRR_URL") or "").split(",")
        if u.strip().strip('\'"').strip()
    ] or None

    # Field validation
    if not GANDI_PAT and not GANDI_API_KEY:
        raise ValueError(
            "Either the GANDI_PAT or the GANDI_API_KEY environment variable is required."
        )

    if GANDI_TTL:
        try:
            GANDI_TTL = int(GANDI_TTL)
        except ValueError:
            raise ValueError("GANDI_TTL must be an integer between 300 and 2592000")
        if GANDI_TTL < 300 or GANDI_TTL > 2592000:
            raise ValueError("GANDI_TTL must be an integer between 300 and 2592000")

    if SHOUTRRR_URLS:
        for u in SHOUTRRR_URLS:
            _log(f"Shoutrrr URL scheme: {u.split('://')[0]}://***")

    # Record updates
    update_a_record()
    update_aaaa_record()
