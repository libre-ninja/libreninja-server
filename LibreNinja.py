from typing import Union

import aiohttp
from logging import info, warning, error
import logging

from uuid import uuid4

import sys
import os

from requestprocessor import REQUEST_HANDLERS, cleanSession
from sessiontools import *

from config import *

#region Request Processing
async def processJSON(json : dict, sessionID :str) -> Union[dict, None]:
    """
    process the JSON-data recieved from the websocket connection. IF the JSON contains in the top-level a variable named
    request, the appropiate request handler function defined in RequestProcessor.REQUEST_HANDLERS is called. If the
    request contains a variable UUID, the request is routed to the appropiate sessions websocket connection.

    :param json: JSON recieved by Websocket handler
    :param sessionID: SessionID of the session sending the Request
    :return: a String Response
    """
    if "request" in json:
        request = json["request"]
        if request in REQUEST_HANDLERS:
            try:
                func = REQUEST_HANDLERS[request]
                result: dict = await func(json, sessionID)
                return result
            except:
                err = sys.exc_info()[1]
                warning("Error processing as JSON:" + str(json) + str(err.args[0]))
    elif "UUID" in json:
        target = json["UUID"]
        json["UUID"] = sessionID
        await sendJSONToUUID(target, json)
        return None
    else:
        warning("Invalid Request:", json)

async def processData(data : str, sessionID : str) -> str:
    """
    process the data recieved from the websocket connection
    :param data: data recieved by Websocket handler
    :param sessionID: SessionID of the session sending the Request
    :return: a String Response
    """
    try:
        request = json.loads(data)
        response = await processJSON(request, sessionID)
        if response is not None:
            return json.dumps(response)
    except RuntimeError as err:
        error("Error processing as JSON:" + data + str(err))

#endregion

#region CleanUp
async def cleanup (sessionID):
    """
    Cleanup the given session after disconnect
    :param sessionID: SessionID to clean up
    :return: None
    """
    await removeSession(sessionID)
    await cleanSession(sessionID)

#endregion

#region WS Handler
async def websocket_handler(request):
    """
    Aiohttp handler for Websocket requests. This Method is executed once for every connecting instance
    :param request:
    :return:
    """
    ws = web.WebSocketResponse()
    sessionID = uuid4().bytes.hex()

    async with SESSIONS_LOCK:
        SESSIONS_LIST[sessionID] = ws

    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                info('REQUESTED TO CLOSE WEBSOCKET FOR SESSION' + sessionID)
                #await ws.close()
            else:
                ret = await processData(msg.data, sessionID)
                if ret is not None:
                    await ws.send_str(ret)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            info('ws connection closed with exception %s' % ws.exception())

    info('websocket connection closed, cleaning up')
    await cleanup(sessionID)
    return ws

#endregion

#region static initialisation

# Set Home Folder
os.chdir(sys.path[0])
app = web.Application()

if DEBUG_LOG:
    logging.basicConfig(filename=DEBUG_LOG_FILE, format=LOG_FORMAT, filemode='a', level=logging.DEBUG)
logging.basicConfig(filename=ERROR_LOG_FILE, format=LOG_FORMAT, filemode='a', level=logging.WARNING)

#region routes
app.add_routes([web.get(LISTEN_PATH, websocket_handler)])
#endregion

#endregion


if __name__ == '__main__':
    web.run_app(app, port=PORT)
