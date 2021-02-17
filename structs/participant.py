from typing import List
from typing import Dict
from logging import debug, info, warning, error, critical
from .seeds import getSeed

import asyncio


class Participant:
    """
    Structure holding all data related to the participant
    """
    def __init__(self, uuid=""):
        """
        Constructor
        :param uuid: UUID aka SessionID of this Participant
        """
        self.lock = asyncio.Lock()
        self.uuid = uuid

        self.roomID = None
        self.streamID = None
        self.title = None

    def setRoom(self, roomID=None):
        """
        Setter for the RoomID of this Participant
        :param roomID: ID of the Room this participant is part of
        :return: None
        """
        self.roomID = roomID

    def getRoom(self):
        """
        :return: the RoomID of this Participants room
        """
        return self.roomID

    def setStreamID(self, streamID=None):
        """
        Sets the StreamID of this Client
        :param streamID: StreamID to set
        :return: None
        """
        self.streamID = streamID

    def getStreamID(self):
        """

        :return: the StreamID this Participant is pushing to
        """
        return self.streamID

    def setTitle(self, title=None):
        """
        Sets the Title of this Participant
        :param title: Title to set
        :return:
        """
        self.title = title

    def getTitle(self):
        """

        :return: the Title of this Participant
        """
        return self.title

    def uuidAsDict(self):
        """

        :return: A Dict containing UUID and StreamID of this participant
        """
        ret = {"UUID": self.uuid}

        if self.streamID is not None:
            ret["streamID"] = self.streamID

        return ret

#region static functions
PARTICIPANTS_LOCK = asyncio.Lock()
"""AIO Lock for list of participants"""
PARTICIPANTS: Dict[str, Participant] = {}
"""
Dict containing Participants, where the key is the uuid of the participant and the value the participant struct for the 
UUID
"""

async def getOrCreateParticipant(uuid) -> Participant:
    """
    Gets a Participant by the given UUID, or creates a new Participant, if none is found
    :param uuid: UUID of the Participant to return
    :return: the PArticipant for the given UUID
    """
    participant = None
    async with PARTICIPANTS_LOCK:
        if uuid not in PARTICIPANTS:
            PARTICIPANTS[uuid] = Participant(uuid=uuid)
        participant = PARTICIPANTS[uuid]
    return participant


async def getParticipant(uuid) -> Participant:
    """
    Gets the Participant with the given UUID
    :param uuid: UUID to look for
    :return: the Participant with the given ID, or None, if not found
    """
    participant = None
    async with PARTICIPANTS_LOCK:
        if uuid in PARTICIPANTS:
            participant = PARTICIPANTS[uuid]
    return participant


async def getParticipantByStreamID(streamID, participantList = None):
    """
    Get the participant by the streamID
    :param streamID: streamID of the participant to fetch
    :param participantList: NOT USED ATM
    :return:
    """
    return getSeed(streamID)
 #   if participantList is None:
 #       async with PARTICIPANTS_LOCK:
 #           return __getParticipantByStreamID(streamID, PARTICIPANTS.values())
 #   else:
 #       return __getParticipantByStreamID(streamID, participantList)


#def __getParticipantByStreamID(streamID: str, participantList=None):
#    for p in participantList:
#        if p.getStreamID() == streamID:
#            return p
#    info("No Participant with the given StreamID found.")
#    return None

#endregion