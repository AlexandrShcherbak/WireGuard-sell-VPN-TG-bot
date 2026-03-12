from pathlib import Path

import qrcode

from wireguard.manager import WireGuardClient

DEFAULT_TEMPLATE = """[Interface]
PrivateKey = {private_key}
Address = {address}
DNS = {dns}

[Peer]
PublicKey = {server_public_key}
AllowedIPs = {allowed_ips}
Endpoint = {endpoint}
PersistentKeepalive = 25
"""


def build_client_config(
    client: WireGuardClient,
    server_public_key: str,
    endpoint: str,
    allowed_ips: str = '0.0.0.0/0, ::/0',
    template: str = DEFAULT_TEMPLATE,
) -> str:
    return template.format(
        private_key=client.private_key,
        address=client.address,
        dns=client.dns,
        server_public_key=server_public_key,
        allowed_ips=allowed_ips,
        endpoint=endpoint,
    )


def save_config(path: str | Path, config_text: str) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(config_text, encoding='utf-8')
    return str(file_path)


def generate_qr(path: str | Path, content: str) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    image = qrcode.make(content)
    image.save(file_path)
    return str(file_path)
