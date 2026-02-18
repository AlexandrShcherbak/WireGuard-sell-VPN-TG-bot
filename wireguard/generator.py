from pathlib import Path

from wireguard.manager import WireGuardClient


def build_client_config(
    client: WireGuardClient,
    server_public_key: str,
    endpoint: str,
    allowed_ips: str = '0.0.0.0/0, ::/0',
) -> str:
    return f"""[Interface]
PrivateKey = {client.private_key}
Address = {client.address}
DNS = {client.dns}

[Peer]
PublicKey = {server_public_key}
AllowedIPs = {allowed_ips}
Endpoint = {endpoint}
PersistentKeepalive = 25
"""


def save_config(path: str | Path, config_text: str) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(config_text, encoding='utf-8')
    return str(file_path)
