from loguru import logger
import bittensor


def get_string_axons(metagraph, uids: list[int] = []) -> list[str]:
    axons: list[bittensor.Axon] = metagraph.axons
    if uids:
        axons = [axons[uid] for uid in uids if uid in metagraph.uids]
    string_axons = [axon.to_string() for axon in axons]
    return string_axons


def get_axons_from_strings(string_axons: list[str]) -> list[bittensor.AxonInfo]:
    axons = [
        bittensor.AxonInfo.from_string(string_axon) for string_axon in string_axons
    ]
    return axons
