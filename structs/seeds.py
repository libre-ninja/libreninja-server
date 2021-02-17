import asyncio

SEED_LOCK = asyncio.Lock()
"""AIO Lock for Seed Dictionary"""
SEED_LIST = {}
"""Dictionary of Seeds"""

async def putSeed (streamID: str, participant):
    """
    Puts the StreamID in the Seed Directory

    :param streamID: StreamID of the Stream to put in the Seed Directory
    :param participant: Participant sending the stream
    :return: None
    """
    async with SEED_LOCK:
        SEED_LIST[streamID] = participant
        async with participant.lock:
            participant.setStreamID(streamID)

async def getSeed (streamID : str):
    """
    Returns the Participant sending the stream with the given ID, or None, if not found
    :param streamID: StreamID to look for
    :return: the Participant sending the stream with the given ID, or None if not found
    """
    async with SEED_LOCK:
        if streamID in SEED_LIST:
            return SEED_LIST[streamID]
    return None