from pydantic import BaseModel
from typing import  Dict

class SetWeightsRequest(BaseModel):
    uids: list[int]
    weights: list[float]
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
    v_permits: list[bool]


class AxonsRequest(BaseModel):
    uids: list[int]


class AxonsResponse(BaseModel):
    uids: list[int]
    axons: list[str]

class RateLimitResponse(BaseModel):
    rate_limits: Dict[int, int]

class RateLimitRequest(BaseModel):
    min_stake: float

class MinerInfoRequest(BaseModel):
    ss58_address: str

class MinerInfoResponse(BaseModel):
    uid: int
    incentive: float
