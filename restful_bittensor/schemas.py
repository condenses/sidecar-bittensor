from pydantic import BaseModel


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
    normalized_stake: list[float]


class ValidatorPermitResponse(BaseModel):
    v_permits: list[bool]


class AxonsRequest(BaseModel):
    uids: list[int]


class AxonsResponse(BaseModel):
    axons: list[str]
