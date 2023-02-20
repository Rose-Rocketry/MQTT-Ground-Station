from quart import Quart, websocket
import asyncio
import paho.mqtt.client as mqtt
import logging
import json

logging.basicConfig(level=logging.INFO)

TOPIC_PREFIX = "sensors/"

app = Quart(__name__, static_folder="dist", static_url_path="")


@app.websocket("/ws")
async def ws() -> None:
    assert (
        asyncio.get_event_loop_policy().get_event_loop() == asyncio.get_running_loop()
    ), "not using default loop!"
    await websocket.accept()

    app.logger.info(
        f"New connection from {websocket.remote_addr}, sending {len(data)} queued packets"
    )

    i = 0
    while True:
        while len(data) <= i:
            # Prevent closed connections from interfering with each other
            await asyncio.shield(new_data)

        await websocket.send(data[i])
        i += 1


@app.get("/")
async def root():
    return await app.send_static_file("index.html")


client = mqtt.Client("dashboard", clean_session=True)
data = []
new_data: asyncio.Future = None


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
        logging.warn(f"Packet already has id key, will be overwritten from {repr(decoded['id'])} to {repr(id)}")
        return

    # Add ID to messages to distinguish sensors
    decoded["id"] = id
    ws_message = json.dumps(decoded)

    loop = new_data.get_loop()
    loop.call_soon_threadsafe(publish_message, ws_message)


def publish_message(ws_message):
    global new_data

    # TODO: memory usage grows forever
    data.append(ws_message)
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
    client.connect_async("rsmb")
    client.loop_start()
    yield
    client.loop_stop()
