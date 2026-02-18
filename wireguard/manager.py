from dataclasses import dataclass

import aiohttp


@dataclass(slots=True)
class WireGuardClient:
    id: str
    name: str
    private_key: str
    address: str
    dns: str


class WireGuardEasyManager:
    """HTTP-клиент для WireGuard Easy API."""

    def __init__(self, api_url: str, api_token: str) -> None:
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token

    @property
    def _headers(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.api_token}', 'Content-Type': 'application/json'}

    async def create_client(self, client_name: str) -> WireGuardClient:
        payload = {'name': client_name}
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.post(f'{self.api_url}/api/wireguard/client', json=payload, timeout=20) as resp:
                resp.raise_for_status()
                data = await resp.json()
        return WireGuardClient(
            id=str(data['id']),
            name=data['name'],
            private_key=data['privateKey'],
            address=data['address'],
            dns=data.get('dns', '1.1.1.1'),
        )

    async def delete_client(self, client_id: str) -> None:
        async with aiohttp.ClientSession(headers=self._headers) as session:
            async with session.delete(f'{self.api_url}/api/wireguard/client/{client_id}', timeout=20) as resp:
                resp.raise_for_status()
