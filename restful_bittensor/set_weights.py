import bittensor as bt
from loguru import logger
from tabulate import tabulate


def set_weights(
    subtensor: bt.Subtensor,
    wallet,
    uids: list[int],
    weights: list[float],
    netuid: int,
    version: int = 1,
) -> tuple[bool, str]:
    logger.info(f"netuid:{netuid}|version:{version}|wallet:{wallet}")

    # Create a preview table of first 5 rows
    preview_data = list(zip(uids, weights))
    table = tabulate(
        preview_data, headers=["UID", "Weight"], tablefmt="grid", floatfmt=".4f"
    )
    logger.info(f"\n{table}")
    try:
        (
            processed_weight_uids,
            processed_weights,
        ) = bt.utils.weight_utils.process_weights_for_netuid(
            uids=uids,
            weights=weights,
            netuid=netuid,
            subtensor=subtensor,
            metagraph=subtensor.metagraph,
        )
    except Exception as e:
        logger.error(f"Error processing weights: {e}")
        return False, str(e)

    try:
        result, msg = subtensor.set_weights(
            netuid=netuid,
            uids=processed_weight_uids,
            weights=processed_weights,
            version=version,
            wallet=wallet,
        )
        logger.info(f"result:{result}|msg:{msg}")
        return result, msg
    except Exception as e:
        logger.error(f"Error setting weights: {e}")
        return False, str(e)
