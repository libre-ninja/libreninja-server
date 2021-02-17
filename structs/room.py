from typing import List
from typing import Dict

import asyncio

from .participant import *

class Room:
    def __init__(self, roomID: str=""):
        """
        Create a new Room
        :param roomID: ID for this Room
        """
        self.lock = asyncio.Lock()
        self.roomID = roomID
        self.director: Participant = None
        self.participants: List[Participant] = []

    def setDirector (self, participant: Participant):
        """
        Sets the main director of this Room
        :param participant:
        :return:
        """
        self.director = participant

    async def joinRoom(self, uuid: str):
        """
        Join the participant with the given uuid to this room

        :param uuid: UUID of the Participant to join
        :return:
        """
        participant = await getOrCreateParticipant(uuid=uuid)
        async with participant.lock:
            participant.setRoom(self.roomID)
            #TODO: Check for doubles
            self.participants.append(participant)

    async def leaveRoom(self, uuid: str):
        """
        Remove the participant with the given uuid from this Room

        :param uuid: UUID of the Participant to remove
        :return:
        """
        participant = await getOrCreateParticipant(uuid=uuid)
        if participant in self.participants:
            async with participant.lock:
                participant.setRoom(None)
                self.participants.remove(participant)
        if participant == self.director:
            self.director = None


ROOMS_LOCK = asyncio.Lock()
"""aio lock for ROOMS"""
ROOMS: Dict[str, Room] = {}
"""List of all Rooms currently active"""