from fastapi import FastAPI, HTTPException
import bittensor as bt
from loguru import logger
from pydantic_settings import BaseSettings
import uvicorn
import asyncio
from typing import Optional

from .metagraph import get_string_axons
from .set_weights import set_weights
from .schemas import (
    SetWeightsRequest,
    SetWeightsResponse,
    LastUpdateResponse,
    NormalizedStakeResponse,
    ValidatorPermitResponse,
    AxonsRequest,
    AxonsResponse,
)
import time
from starlette.concurrency import run_in_threadpool


class Settings(BaseSettings):
    network: str = "finney"
    netuid: int = 47
    wallet_name: str = "default"
    wallet_path: str = "~/.bittensor/wallets"
    wallet_hotkey: str = "default"
    host: str = "0.0.0.0"
    port: int = 9100

    class Config:
        # Optionally, you can use a .env file for configuration
        env_file = ".env"
        extra = "ignore"


# Load settings from environment variables (with defaults as fallback)
settings = Settings()

from rich.console import Console
from rich.panel import Panel

console = Console()
settings_dict = settings.model_dump()

for section, values in settings_dict.items():
    console.print(
        Panel.fit(
            str(values),
            title=f"[bold blue]{section}[/bold blue]",
            border_style="green",
        )
    )

# Initialize bittensor objects using the settings
SUBTENSOR = bt.Subtensor(network=settings.network)
METAGRAPH = SUBTENSOR.metagraph(netuid=settings.netuid)
WALLET = bt.wallet(
    name=settings.wallet_name,
    path=settings.wallet_path,
    hotkey=settings.wallet_hotkey,
)
DENDRITE = bt.Dendrite(
    wallet=WALLET,
)
LAST_UPDATE = 0
TEMPO = 360
# Create FastAPI app instance with custom metadata
app = FastAPI(
    title="Restful Bittensor API",
    description=f"""A RESTful API for interacting with the Bittensor metagraph and managing weight settings.

Current Settings:
- Network: {settings.network}
- NetUID: {settings.netuid}
- Wallet: {settings.wallet_name}
- Hotkey: {settings.wallet_hotkey}
- Host: {settings.host}
- Port: {settings.port}
""",
    version="1.0.0",
)

# Global variable to store the background task
SYNC_TASK: Optional[asyncio.Task] = None


@app.on_event("startup")
async def startup_event() -> None:
    """
    Operations to run during the startup event.
    Initializes periodic metagraph sync.
    """
    global SYNC_TASK

    async def sync_metagraph():
        while True:
            try:
                logger.info("Syncing metagraph...")
                METAGRAPH.sync()
                logger.info("Metagraph sync complete")
                await asyncio.sleep(120)  # Sync every 2 minutes
            except Exception as e:
                logger.error(f"Error syncing metagraph: {e}")
                await asyncio.sleep(
                    30
                )  # Wait 30 seconds before retrying if there's an error

    SYNC_TASK = asyncio.create_task(sync_metagraph())
    logger.info("FastAPI application startup complete.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Operations to run during the shutdown event.
    Cancels the metagraph sync task.
    """
    global SYNC_TASK
    if SYNC_TASK:
        SYNC_TASK.cancel()
        try:
            await SYNC_TASK
        except asyncio.CancelledError:
            pass
    logger.info("FastAPI application shutdown complete.")


@app.post(
    "/api/metagraph/axons",
    response_model=AxonsResponse,
    tags=["Metagraph"],
    summary="Retrieve Axons",
)
async def get_axons(request: AxonsRequest) -> AxonsResponse:
    """
    Retrieve axons (string representations) for the provided uids.
    """
    logger.info(f"getting axons for {request.uids}")
    try:
        axons = get_string_axons(METAGRAPH, request.uids)
        return AxonsResponse(axons=axons)
    except Exception as e:
        logger.error(f"Error getting axons: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting axons: {e}")


@app.get(
    "/api/metagraph/last-update",
    response_model=LastUpdateResponse,
    tags=["Metagraph"],
    summary="Get Last Updates",
)
async def get_last_update() -> LastUpdateResponse:
    """
    Retrieve the last update timestamps for the provided uids.
    """
    try:
        neuron_uid = METAGRAPH.hotkeys.index(WALLET.hotkey.ss58_address)
        last_update = METAGRAPH.last_update[neuron_uid]
    except KeyError as e:
        logger.error(f"UID not found in metagraph: {e}")
        raise HTTPException(status_code=404, detail=f"UID not found: {e}")
    return LastUpdateResponse(last_update=last_update)


@app.get(
    "/api/metagraph/normalized-stake",
    response_model=NormalizedStakeResponse,
    tags=["Metagraph"],
    summary="Normalized Stake",
)
async def get_normalized_stake() -> NormalizedStakeResponse:
    """
    Retrieve the normalized stakes across all nodes.
    """
    try:
        logger.info(f"getting normalized stake")
        stakes = METAGRAPH.S
        total_stake = sum(stakes)
        if total_stake == 0:
            logger.error("Total stake is zero, cannot calculate normalized stake.")
            raise HTTPException(
                status_code=400, detail="Total stake is zero; cannot normalize stakes."
            )
        neuron_uid = METAGRAPH.hotkeys.index(WALLET.hotkey.ss58_address)
        normalized_stake = stakes[neuron_uid] / total_stake
        logger.info(f"normalized stake: {normalized_stake}")
    except Exception as e:
        logger.error(f"Error getting normalized stake: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting normalized stake: {e}"
        )
    return NormalizedStakeResponse(normalized_stake=normalized_stake)


@app.post(
    "/api/metagraph/validator-permit",
    response_model=ValidatorPermitResponse,
    tags=["Metagraph"],
    summary="Validator Permits",
)
async def get_validator_permit() -> ValidatorPermitResponse:
    """
    Retrieve the validator permits from the metagraph.
    """
    v_permits = METAGRAPH.v_permits
    return ValidatorPermitResponse(v_permits=v_permits)


@app.post(
    "/api/set-weights",
    response_model=SetWeightsResponse,
    tags=["Weights"],
    summary="Set Weights",
)
async def set_weights_endpoint(request: SetWeightsRequest) -> SetWeightsResponse:
    """
    Set the weights for specified nodes in the network.
    """
    NEURON_UID = METAGRAPH.hotkeys.index(WALLET.hotkey.ss58_address)
    current_block = SUBTENSOR.get_current_block()
    LAST_UPDATE = METAGRAPH.last_update[NEURON_UID]
    if current_block - LAST_UPDATE > TEMPO:
        result, msg = await run_in_threadpool(
            set_weights,
            subtensor=SUBTENSOR,
            wallet=WALLET,
            uids=request.uids,
            weights=request.weights,
            netuid=request.netuid,
            version=request.version,
        )
        if result:
            await run_in_threadpool(METAGRAPH.sync)
    else:
        result = False
        msg = f"Not enough time has passed to set weights. {TEMPO - (current_block - LAST_UPDATE)} blocks remaining."
    return SetWeightsResponse(result=result, msg=msg)


@app.get("/api/signature-headers")
def get_signature_headers() -> dict:
    """
    Get the signature headers for the validator.
    """
    nonce = str(time.time_ns())
    signature = f"0x{DENDRITE.keypair.sign(nonce).hex()}"
    return {
        "validator-hotkey": WALLET.hotkey,
        "signature": signature,
        "nonce": nonce,
        "netuid": settings.netuid,
        "Content-Type": "application/json",
    }


def start_server() -> None:
    """
    Starts the FastAPI server using uvicorn.
    """
    uvicorn.run(
        "restful_bittensor.server:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Change to True for development if needed.
    )


if __name__ == "__main__":
    start_server()
