
<br /><br />

<div align="center">
  <h1 align="center">restful-bittensor</h1>
  <h4 align="center"> REST service that makes it easy to interact with Subtensor Blockchain.
</div>

## Installation

```bash
pip install restful-bittensor
```

## Environment Variables

```bash
export NETWORK=finney
export NETUID=47
export WALLET_NAME=default
export WALLET_PATH=~/.bittensor/wallets
export WALLET_HOTKEY=default
export RESTFUL_SUBTENSOR_HOST=0.0.0.0
export RESTFUL_SUBTENSOR_PORT=9100
```

## Usage

### Server
```bash
rb-start-server
```

### Client

The package provides both synchronous and asynchronous clients for interacting with the REST API.

#### Synchronous Client
```python
from restful_bittensor import RestfulBittensor

# Using context manager (recommended)
with RestfulBittensor("http://localhost:9100") as client:
    # Get axons for specific UIDs
    axons = client.get_axons([1, 2, 3])
    
    # Get last update timestamps
    last_updates = client.get_last_update([1, 2, 3])
    
    # Get normalized stake for all neurons
    stakes = client.get_normalized_stake()
    
    # Get validator permits
    permits = client.get_validator_permit()
    
    # Set weights
    success, message = client.set_weights(
        uids=[1, 2, 3],
        weights=[0.3, 0.3, 0.4],
        netuid=1
    )

```

#### Async Client
```python
from restful_bittensor import AsyncRestfulBittensor
import asyncio

async def main():
    async with AsyncRestfulBittensor("http://localhost:9100") as client:
        # Get axons for specific UIDs
        axons = await client.get_axons([1, 2, 3])
        
        # Get last update timestamps
        last_updates = await client.get_last_update([1, 2, 3])
        
        # Get normalized stake for all neurons
        stakes = await client.get_normalized_stake()
        
        # Get validator permits
        permits = await client.get_validator_permit()
        
        # Set weights
        success, message = await client.set_weights(
            uids=[1, 2, 3],
            weights=[0.3, 0.3, 0.4],
            netuid=1
        )

# Run the async function
asyncio.run(main())
```

All client methods will raise an `httpx.HTTPError` if the server returns an error status code.
