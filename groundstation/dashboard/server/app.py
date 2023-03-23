from quart import Quart, websocket
from collections import deque
import asyncio
import paho.mqtt.client as mqtt
import logging
import json

logging.basicConfig(level=logging.INFO)

TOPIC_PREFIX = "sensors/"

HISTORY_LENGTH = 1000
history_meta: dict[str, dict] = dict()
history_data: dict[str, deque[dict]] = dict()
new_data: asyncio.Future = None

app = Quart(__name__, static_folder="dist", static_url_path="")


@app.websocket("/ws")
async def ws() -> None:
    assert (
        asyncio.get_event_loop_policy().get_event_loop() == asyncio.get_running_loop()
    ), "not using default loop!"
    await websocket.accept()

    est_history_length = sum(len(q) for q in history_data.values()) + len(history_meta)
    await websocket.send_json({
        "initial_history": est_history_length
    })

    app.logger.info(
        f"New connection from {websocket.remote_addr}, sending {est_history_length} history packets"
    )

    if est_history_length > 0:
        for packet in history_meta.values():
            await websocket.send(packet)

        for sensor in history_data.values():
            # This list conversion prevents the error "RuntimeError: deque mutated during iteration"
            # It may cause the client to loose a few packets if they load too slowly
            for packet in list(sensor): 
                await websocket.send(packet)
                

        await websocket.send_json({
            "initial_history": 0
        })

    while True:
        # TODO: Send History

        await websocket.send(await asyncio.shield(new_data))


@app.get("/")
async def root():
    return await app.send_static_file("index.html")


client = mqtt.Client("dashboard", clean_session=True)

def on_mqtt_message(client, _, message: mqtt.MQTTMessage):
    id = message.topic.removeprefix(TOPIC_PREFIX)

    decoded = json.loads(message.payload)
    if type(decoded) != dict:
        logging.warn(f"Only JSON objects are supported, found {repr(decoded)}")
        return

    if "data" not in decoded and "meta" not in decoded:
        logging.warn(f"Packet has neither data nor meta, found {repr(decoded)}")
        return

    if "id" in decoded:
        logging.warn(
            f"Packet already has id key, will be overwritten from {repr(decoded['id'])} to {repr(id)}"
        )
        return

    # Add ID to messages to distinguish sensors
    decoded["id"] = id
    ws_message = json.dumps(decoded)

    loop = new_data.get_loop()
    loop.call_soon_threadsafe(publish_message, ws_message, id, "meta" in decoded)


def publish_message(ws_message, id, is_meta):
    global new_data

    # TODO: memory usage grows forever
    if is_meta:
        history_meta[id] = ws_message
    else:
        q = history_data.get(id)
        if q == None:
            q = deque(maxlen=HISTORY_LENGTH)
            history_data[id] = q
        q.append(ws_message)

    new_data.set_result(ws_message)
    new_data = asyncio.Future()


def on_mqtt_connect(client, _, flags, rc):
    client.subscribe(TOPIC_PREFIX + "#", qos=0)


@app.while_serving
async def manage_client_thread():
    global new_data

    new_data = asyncio.Future()

    client.enable_logger(app.logger)
    client.on_message = on_mqtt_message
    client.on_connect = on_mqtt_connect
    client.connect_async("10.82.104.3")
    client.loop_start()
    yield
    client.loop_stop()
