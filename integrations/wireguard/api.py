from typing import Protocol


class WireGuardApiClient(Protocol):
    async def create_client(self, user_id: int) -> dict:
        ...

    async def revoke_client(self, client_id: str) -> None:
        ...


class StubWireGuardApiClient:
    """Временная заглушка для внешнего WireGuard API."""

    async def create_client(self, user_id: int) -> dict:
        return {
            "client_id": f"stub-client-{user_id}",
            "config": "# stub wireguard config",
        }

    async def revoke_client(self, client_id: str) -> None:
        return None
