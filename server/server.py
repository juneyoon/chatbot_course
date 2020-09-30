import asyncio
import json
import logging
import websockets
import ssl
import time

from library.helpers import *
from actions import process_message

from pprint import pprint

logging.basicConfig()

STATE = {}
CONNECTIONS = {}


async def register(websocket):
    connection_id = time.time()
    CONNECTIONS[connection_id] = websocket
    STATE[connection_id] = new_state()
    await websocket.send(json.dumps({
        "type": "connection_id",
        "connection_id": connection_id
    }))
    return connection_id


async def unregister(connection_id):
    #CONNECTIONS.remove(connection_id)
    pass

async def counter(websocket, path):
    print("New Connection")
    connection_id = await register(websocket)
    connection_await = True
    res = await websocket.recv()
    res = json.loads(res)
    first_message = {
        "type": "first_message",
        "message": "Hi, I'm a food order bot. I can help you choose. Would you like to order something?"
    }
    if res.get("language_code"):
        STATE[connection_id]['language'] = res.get("language_code")
    if res.get("connection_id"):
        past_connection_id = res.get("connection_id")
        if past_connection_id != connection_id:
            if STATE.get(past_connection_id):
                STATE[connection_id] = STATE[past_connection_id]
            else:
                await websocket.send(json.dumps(process_translation_to_user(STATE[connection_id], first_message)))
        else:
            await websocket.send(json.dumps(process_translation_to_user(STATE[connection_id], first_message)))
    try:
        async for message in websocket:
            message_data = json.loads(message)
            if message_data.get("language_code"):
                STATE[connection_id] = new_state()
                STATE[connection_id]['language'] = message_data.get("language_code")
                await websocket.send(json.dumps(process_translation_to_user(STATE[connection_id], first_message)))
            if message_data.get("message"):
                result = process_message(STATE[connection_id], message_data, connection_id)
                await websocket.send(json.dumps(result))
    finally:
        await unregister(connection_id)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
start_server = websockets.serve(counter, None, 6789, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
