<script setup lang="ts">
import { reactive, ref, toRaw } from 'vue'
import DashboardView from './components/DashboardView.vue'
import { DecompressionStream } from "@stardazed/streams-compression";
import type { Packet, SensorData } from './protocol'

type State = "main" | "loading" | "loaded"

const defaultWsURL = `${window.location.protocol.replace("http", "ws")}//${window.location.host}/ws`
const HISTORY_LENGTH = 1000

let state = ref<State>("main")
let connectionType = ref<"ws" | "file">("ws")

let wsInput = ref(defaultWsURL)
let wsError = ref(false)
let wsConnection: WebSocket
let wsHistoryRead = ref(0)
let wsHistoryLength = ref(0)

let fileLoadPercent = ref(0)

function connectTo(url: string) {
  if (state.value != "main") {
    return
  }

  state.value = "loading"
  connectionType.value = "ws"
  wsError.value = false
  resetSensors()

  wsConnection = new WebSocket(url)
  wsConnection.onerror = (e) => {
    state.value = "main";
    wsError.value = true;
  }
  wsConnection.onmessage = (e) => handlePacket(JSON.parse(e.data))
  wsConnection.onclose = (e) => state.value = 'main'
}

async function loadFile() {
  if (state.value != "main") {
    return
  }

  const input = document.getElementById("fileInput") as HTMLInputElement
  const file = input.files?.[0];
  if (!file) {
    return
  }

  state.value = "loading"
  connectionType.value = "file"
  resetSensors()

  try {
    await iterateTextFileLines(file, line => {
      try {
        handlePacket(JSON.parse(line))
      } catch (error) {
        // TODO: Show warning
        console.error("Error handing line", line, error)
      }
    }, percent => {
      fileLoadPercent.value = percent
    })

    state.value = "loaded"
  } catch (error) {
    console.error(error);
    state.value = "main"
  }
}

// Based on code from https://developer.mozilla.org/en-US/docs/Web/API/ReadableStreamDefaultReader/read
async function iterateTextFileLines(file: File, cb: (line: string) => void, progress: (percent: number) => void) {
  const utf8Decoder = new TextDecoder("utf-8");


  let stream: ReadableStream = file.stream()

  let bytesTotal = file.size
  let bytesRead = 0

  let progressTransform = new TransformStream<Uint8Array, Uint8Array>({
    transform(chunk, controller) {
      bytesRead += chunk.length
      progress(bytesRead / bytesTotal * 100)
      controller.enqueue(chunk)
    }
  })

  stream = stream.pipeThrough(progressTransform)

  let magicBytes = new Uint8Array(await file.slice(0, 2).arrayBuffer())
  if (magicBytes[0] == 0x1f && magicBytes[1] == 0x8b) {
    console.log("GZIP detected, wrapping in decompress")
    stream = stream.pipeThrough(new DecompressionStream("gzip"))
  }

  let reader = stream.getReader()

  let { value: chunkRaw, done: readerDone } = await reader.read();
  let chunk = chunkRaw ? utf8Decoder.decode(chunkRaw, { stream: true }) : "";

  let startIndex = 0;

  while (true) {
    let lnIndex = chunk.indexOf("\n", startIndex);
    if (lnIndex < 0) {
      if (readerDone) {
        break;
      }
      let remainder = chunk.substring(startIndex);
      ({ value: chunkRaw, done: readerDone } = await reader.read());
      chunk = remainder + (chunkRaw ? utf8Decoder.decode(chunkRaw, { stream: true }) : "");
      startIndex = 0;
      continue;
    }
    cb(chunk.substring(startIndex, lnIndex));
    startIndex = lnIndex + 1;
  }
  if (startIndex < chunk.length) {
    // last line didn't end in a newline char
    cb(chunk.substring(startIndex));
  }
}


let sensorOrder = ref<string[]>([])
let sensorMap = reactive(new Map<string, SensorData>())

function resetSensors() {
  sensorOrder.value = []
  sensorMap.clear()
}

function handlePacket(packet: Packet) {
  if (state.value == "loading" && connectionType.value == "ws") {
    if ('initial_history' in packet) {
      if (packet.initial_history == 0) {
        state.value = "loaded"
        return
      } else {
        wsHistoryLength.value = packet.initial_history!
        return
      }
    }

    wsHistoryRead.value++
  }

  if (typeof packet.id != "string") {
    console.warn("Packet has no id", packet)
    return
  }
  const id = packet.id

  if (!sensorOrder.value.includes(id)) {
    sensorOrder.value.push(id)
    sensorOrder.value.sort()
  }


  if ('meta' in packet) {
    let sensor = sensorMap.get(id)
    if (!sensor) {
      console.log("New sensor", id)
      // New sensor
      sensor = {
        id,
        meta: null!,
        channelMap: new Map(),
      };
      sensorMap.set(id, sensor);
    }
    sensor.meta = packet.meta!
    sensor.channelOrder = sensor.meta.channels.map(ch => ch.key)

    for (const ch of sensor.meta.channels) {
      const channel = sensor.channelMap.get(ch.key)
      if (channel) {
        // Existing channel
        channel.meta = ch;
      } else {
        // New channel
        sensor.channelMap.set(ch.key, {
          key: ch.key,
          meta: ch,
          series: [],
          timestamps: []
        })
      }
    }
  }

  if ('data' in packet) {
    let sensor = sensorMap.get(id)

    if (!('timestamp' in packet.data)) {
      console.warn("Packet missing timestamp", packet)
      return
    }

    if (!sensor) {
      // No metadata, guess
      sensor = {
        id: id,
        channelMap: new Map()
      }
      sensorMap.set(id, sensor);
    }

    for (const key in packet.data) {
      if (key == "timestamp") continue

      let channel = sensor.channelMap.get(key)
      if (!channel) {
        channel = {
          key,
          timestamps: [],
          series: [],
        }
        sensor.channelMap.set(key, channel)
      }

      let data = packet.data[key]
      if (!Array.isArray(data)) {
        data = [data]
      }
      channel.timestamps.push(new Date(packet.data.timestamp * 1000))

      if (connectionType.value == "ws" && channel.timestamps.length > HISTORY_LENGTH) {
        channel.timestamps.shift()
        channel.series.map(x => x.shift())
      }

      const sampleI = channel.timestamps.length - 1
      for (let seriesI = 0; seriesI < data.length; seriesI++) {
        let list = channel.series[seriesI] ?? []
        list[sampleI] = data[seriesI]
        channel.series[seriesI] = list
      }
    }
  }
}
</script>

<template>
  <i-layout>
    <i-layout-content v-if="state == 'main' || state == 'loading'">
      <i-container>
        <h1>Rose-Rocketry Dashboard</h1>
        <i-row>
          <i-column xl="6">
            <h2>Connect to rocket</h2>
            <i-input :plaintext="state == 'loading'" v-model="wsInput" @keyup.enter="connectTo(wsInput)"
              :placeholder="defaultWsURL">
              <template #append>
                <i-button :loading="state == 'loading' && connectionType == 'ws'" :disabled="state == 'loading'"
                  @click="connectTo(wsInput)">Connect</i-button>
              </template>
            </i-input>
            <i-progress v-if="state == 'loading' && connectionType == 'ws'">
              <i-progress-bar color="success" :value="100 * wsHistoryRead / wsHistoryLength" />
            </i-progress>
            <i-alert v-if="wsError && connectionType == 'ws'" class="_margin-top:1/2" color="danger">
              <template #icon>
                <i-icon name="ink-danger" />
              </template>
              <p>Error occured connecting to WebSocket</p>
            </i-alert>
          </i-column>
        </i-row>
        <i-row>
          <i-column xl="6">
            <h2>Open flight logs</h2>
            <i-input :disabled="state == 'loading'" type="file" id="fileInput">
              <template #append>
                <i-button :loading="state == 'loading' && connectionType == 'file'" :disabled="state == 'loading'"
                  @click="loadFile()">Load File</i-button>
              </template>
            </i-input>
            <i-progress v-if="state == 'loading' && connectionType == 'file'">
              <i-progress-bar color="success" :value="fileLoadPercent" />
            </i-progress>
          </i-column>
        </i-row>
      </i-container>
      <!-- <DashboardView></DashboardView> -->
    </i-layout-content>
    <DashboardView v-else :sensorOrder="sensorOrder" :sensorMap="sensorMap" />
  </i-layout>
</template>
