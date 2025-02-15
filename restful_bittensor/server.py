from fastapi import FastAPI
from pydantic import BaseModel
import os
import bittensor as bt
from .metagraph import get_string_axons
from .set_weights import set_weights
import uvicorn
from loguru import logger

logger.info(bt.__version__)


class SetWeightsRequest(BaseModel):
    uids: list[int]
    weights: list[float]
    netuid: int
    version: int = 1


class SetWeightsResponse(BaseModel):
    result: bool
    msg: str


class AxonsRequest(BaseModel):
    uids: list[int]


class AxonsResponse(BaseModel):
    axons: list[str]


# Initialize environment variables
NETWORK = os.getenv("NETWORK", "finney")
NETUID = int(os.getenv("NETUID", 47))
WALLET_NAME = os.getenv("WALLET_NAME", "default")
WALLET_PATH = os.getenv("WALLET_PATH", "~/.bittensor/wallets")
WALLET_HOTKEY = os.getenv("HOTKEY", "default")
HOST = os.getenv("RESTFUL_SUBTENSOR_HOST", "0.0.0.0")
PORT = int(os.getenv("RESTFUL_SUBTENSOR_PORT", 9100))


app = FastAPI()

# Initialize with global vars and log summary
SUBTENSOR = bt.Subtensor(network=NETWORK)
METAGRAPH = SUBTENSOR.metagraph(netuid=NETUID)
WALLET = bt.wallet(
    name=WALLET_NAME,
    path=WALLET_PATH,
    hotkey=WALLET_HOTKEY,
)

logger.info(f"Server initialized with:")
logger.info(f"Network: {NETWORK}")
logger.info(f"Netuid: {NETUID}")
logger.info(f"Wallet: {WALLET_NAME}")
logger.info(f"Hotkey: {WALLET_HOTKEY}")
logger.info(f"Host: {HOST}")
logger.info(f"Port: {PORT}")


@app.post("/api/metagraph/axons")
async def api_get_axons(request: AxonsRequest):
    return AxonsResponse(axons=get_string_axons(METAGRAPH, request.uids))


@app.post("/api/set_weights")
async def api_set_weights(request: SetWeightsRequest):
    result, msg = set_weights(
        subtensor=SUBTENSOR,
        wallet=WALLET,
        uids=request.uids,
        weights=request.weights,
        netuid=request.netuid,
        version=request.version,
    )
    return SetWeightsResponse(result=result, msg=msg)


def start_server():
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )
