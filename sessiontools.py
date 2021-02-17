import asyncio
import json
from typing import Dict, List

from aiohttp import web

from structs.participant import Participant

#region Session Management Vars

SESSIONS_LOCK = asyncio.Lock()
"""AIO Lock for the Sessions List"""
SESSIONS_LIST: Dict[str, web.WebSocketResponse] = {}
"""List of Sessions currently known to the server"""
#endregion

#region Session Tools
async def removeSession(sessionID):
    """
    Remove the session with the given ID from the list of sessions

    :param sessionID: SessionID to Remove
    :return:None
    """
    async with SESSIONS_LOCK:
        SESSIONS_LIST.pop(sessionID)

async def sendJSONToUUID(uuid, message : dict):
    """
    Sends the given JSON to the Client with the given UUID

    :param uuid: UUID aka SessionID to send the message to
    :param message: message to send (Dictionary)
    :return: None
    """
    if message is not None:
        msg = json.dumps(message)
        async with SESSIONS_LOCK:
            await SESSIONS_LIST[uuid].send_str(msg)

async def sendJSONToParticipants(participants : List[Participant], message, blacklist=None):
    """
    Send JSON to all participants in the given list, excluding those whose uuid is on the blacklist

    :param participants: List of participants to send the message to
    :param message: message to send
    :param blacklist: None or list of UUIDs
    :return: None
    """
    if blacklist is not None:
        list = []
        for p in participants:
            if p.uuid not in blacklist:
                list.append(p)
        await __sendJSONToParticipants(list, message)
    else:
        await __sendJSONToParticipants(participants, message)

async def __sendJSONToParticipants(participants : List[Participant], message):
    """
    Send JSON to all participants in the given list

    :param participants: List of participants to send the message to
    :param message: message to send

    :return: None
    """
    if message is not None:
        msg = json.dumps(message)
        async with SESSIONS_LOCK:
            for participant in participants:
                await SESSIONS_LIST[participant.uuid].send_str(msg)
#endregion