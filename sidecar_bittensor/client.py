from typing import List, Tuple, Optional,Dict
import httpx
from pydantic import BaseModel


class SetWeightsRequest(BaseModel):
    uids: List[int]
    weights: List[float]
    netuid: int
    version: int = 1


class SetWeightsResponse(BaseModel):
    result: bool
    msg: str


class LastUpdateResponse(BaseModel):
    last_update: int


class NormalizedStakeResponse(BaseModel):
    normalized_stake: float


class ValidatorPermitResponse(BaseModel):
    v_permits: List[bool]


class AxonsResponse(BaseModel):
    axons: List[str]


class RateLimitRequest(BaseModel):
    min_stake: float


class RateLimitResponse(BaseModel):
    rate_limits: Dict[int, int]


class MinerInfoRequest(BaseModel):
    ss58_address: str


class MinerInfoResponse(BaseModel):
    uid: int
    incentive: float

class RestfulBittensor:
    def __init__(self, base_url: str = "http://localhost:9100"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client()

    def get_axons(self, uids: List[int]) -> List[str]:
        response = self.client.post(
            f"{self.base_url}/api/metagraph/axons", json={"uids": uids}
        )
        response.raise_for_status()
        return AxonsResponse(**response.json()).axons

    def get_last_update(self) -> int:
        response = self.client.get(f"{self.base_url}/api/metagraph/last-update")
        response.raise_for_status()
        return LastUpdateResponse(**response.json()).last_update

    def get_normalized_stake(self) -> float:
        response = self.client.get(f"{self.base_url}/api/metagraph/normalized-stake")
        response.raise_for_status()
        return NormalizedStakeResponse(**response.json()).normalized_stake

    def get_validator_permit(self) -> List[bool]:
        response = self.client.post(f"{self.base_url}/api/metagraph/validator-permit")
        response.raise_for_status()
        return ValidatorPermitResponse(**response.json()).v_permits

    def set_weights(
        self, uids: List[int], weights: List[float], netuid: int, version: int = 1
    ) -> Tuple[bool, str]:
        response = self.client.post(
            f"{self.base_url}/api/set-weights",
            json={
                "uids": uids,
                "weights": weights,
                "netuid": netuid,
                "version": version,
            },
        )
        response.raise_for_status()
        result = SetWeightsResponse(**response.json())
        return result.result, result.msg

    def get_rate_limit(self, min_stake: float) -> Dict[int, int]:
        response = self.client.post(
            f"{self.base_url}/api/build-rate-limit",
            json={"min_stake": min_stake}
        )
        response.raise_for_status()
        data = RateLimitResponse(**response.json())
        return data.rate_limits

    def get_miner_info(self, ss58_address: str) -> Tuple[int, float]:
        response = self.client.post(
            f"{self.base_url}/api/miner-info",
            json={"ss58_address": ss58_address}
        )
        response.raise_for_status()
        data = MinerInfoResponse(**response.json())
        return data.uid, data.incentive

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class AsyncRestfulBittensor:
    def __init__(self, base_url: str = "http://localhost:9100"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient()

    async def get_axons(self, uids: List[int]) -> List[str]:
        response = await self.client.post(
            f"{self.base_url}/api/metagraph/axons", json={"uids": uids}
        )
        response.raise_for_status()
        return AxonsResponse(**response.json()).axons

    async def get_last_update(self, timeout: int = 10) -> int:
        response = await self.client.get(
            f"{self.base_url}/api/metagraph/last-update", timeout=timeout
        )
        response.raise_for_status()
        return LastUpdateResponse(**response.json()).last_update

    async def get_normalized_stake(self, timeout: int = 10) -> float:
        response = await self.client.get(
            f"{self.base_url}/api/metagraph/normalized-stake", timeout=timeout
        )
        response.raise_for_status()
        return NormalizedStakeResponse(**response.json()).normalized_stake

    async def get_validator_permit(self) -> List[bool]:
        response = await self.client.post(
            f"{self.base_url}/api/metagraph/validator-permit"
        )
        response.raise_for_status()
        return ValidatorPermitResponse(**response.json()).v_permits

    async def set_weights(
        self, uids: List[int], weights: List[float], netuid: int, version: int = 1
    ) -> Tuple[bool, str]:
        response = await self.client.post(
            f"{self.base_url}/api/set-weights",
            json={
                "uids": uids,
                "weights": weights,
                "netuid": netuid,
                "version": version,
            },
        )
        response.raise_for_status()
        result = SetWeightsResponse(**response.json())
        return result.result, result.msg

    async def get_rate_limit(self, min_stake: float) -> Dict[int, int]:
        response = await self.client.post(
            f"{self.base_url}/api/build-rate-limit",
            json={"min_stake": min_stake}
        )
        response.raise_for_status()
        data = RateLimitResponse(**response.json())
        return data.rate_limits

    async def get_miner_info(self, ss58_address: str) -> Tuple[int, float]:
        response = await self.client.post(
            f"{self.base_url}/api/miner-info",
            json={"ss58_address": ss58_address}
        )
        response.raise_for_status()
        data = MinerInfoResponse(**response.json())
        return data.uid, data.incentive

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
