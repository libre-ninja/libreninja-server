from typing import Union

from structs.room import *
from structs.participant import *
from structs.seeds import *
from config import ALLOW_VERSION_CMD
from sessiontools import sendJSONToParticipants

async def onJoinRoom (json : dict, sessionID : str):
    """
    Handles Join Room requests

    :param json: the parsed JSON of the request
    :param sessionID: Session ID
    :return: a listing request, listing all UUIDs in this Room
    """
    list = []
    id = json["roomid"]
    async with ROOMS_LOCK:
        if id in ROOMS:
            for p in ROOMS[id].participants:
                list.append(p.uuidAsDict())
            await sendJSONToParticipants(ROOMS[id].participants, {"request": "someonejoined", "roomID": id, "UUID": sessionID})
        else:
            ROOMS[id] = Room(roomID=id)
        await ROOMS[id].joinRoom(sessionID)
    return {"request": "listing", "list": list, "roomID": id}


async def onClaim (json : dict, sessionID : str):
    """
    Handles Claim Room Requests

    :param json: the parsed JSON of the request
    :param sessionID: Session ID
    :return:
    """
    participant = await getParticipant(sessionID)
    roomID = participant.getRoom()
    room : Union[Room, None] = None

    async with ROOMS_LOCK:
        if roomID in ROOMS:
            room = ROOMS[roomID]
    if room is not None:
        async with room.lock:
            room.setDirector(participant)
    return None


async def onSeed (json : dict, sessionID : str):
    """
    Handles Claim Room Requests

    :param json: the parsed JSON of the request
    :param sessionID: Session ID
    :return: None
    """
    title = json["title"]
    streamID = json["streamID"]

    participant : Participant = await getOrCreateParticipant(uuid=sessionID)
    participant.setTitle(title)
    await putSeed(streamID, participant)

    async with ROOMS_LOCK:
        roomID = participant.getRoom()

        msg = {"request": "videoaddedtoroom",
               "roomID": roomID,
               "UUID": sessionID,
               "streamID": streamID}

        await sendJSONToParticipants(ROOMS[roomID].participants, msg, blacklist=[sessionID])

    return None


async def onPlay (json : dict, sessionID : str):
    """
    Handles Play Requests

    :param json: the parsed JSON of the request
    :param sessionID: Session ID
    :return: None
    """
    streamID = json["streamID"]

    other = await getSeed(streamID)
    if other is not None:
        await sendJSONToParticipants([other], {"request": "offerSDP", "UUID": sessionID})

async def onSendRoom (json : dict, sessionID : str):
    """
    Handles SendRoom Requests

    :param json: the parsed JSON of the request
    :param sessionID: Session ID
    :return: None
    """
    #TODO: [FEATURE_IMPROVEMENT] Buffer SendRoom Requests per Type and Target, and send them to newly joined Sessions
    roomID = json["roomid"]
    room = None
    async with ROOMS_LOCK:
        room = ROOMS[roomID]
    if room is not None:
        async with room.lock:
            await sendJSONToParticipants(room.participants, json, blacklist=[sessionID])

async def onLibreNinjaVersion (json : dict, sessionID : str):
    """
    Answers a libreninja-version request with the current software version of this server

    :param json:
    :param sessionID:
    :return: the currently running version of this server
    """
    if not ALLOW_VERSION_CMD:
        return None
    return {"software": "LibreNinja Server",
            "version": "0.01 Alpha",
            "ninjalevel": "6"}


async def cleanSession (sessionID : str):
    """
    Cleans the Participants associated with the given Session ID
    :param sessionID: Session ID to clean
    :return: None
    """
    participant : Participant = await getParticipant(sessionID)
    if participant is not None:
        roomID = participant.getRoom()
        if roomID is not None:
            await ROOMS[roomID].leaveRoom(sessionID)

REQUEST_HANDLERS = {
    "joinroom": onJoinRoom,
    "claim": onClaim,
    "seed": onSeed,
    "play": onPlay,
    "sendroom": onSendRoom,
    "libreninja-version": onLibreNinjaVersion
}
"""
    Dictionary containing all request handler functions. Key is the string value of "request" in the json message the 
    handler function should handle, value is a function taking a dictionary containing the parsed json, and a string 
    containing the sessionID of the session that send the request
"""