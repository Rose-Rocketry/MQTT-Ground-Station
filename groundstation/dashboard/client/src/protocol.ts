import { ref, type Ref, type ShallowRef } from "vue"

export interface Packet {
  id: string
  meta?: Metadata
  data?: any
  initial_history?: number
}

export interface Metadata {
  name: string
  channels: MetadataChannel[]
}

type ChannelType = "number" | "vector" | "string" | "bool"

export interface MetadataChannel {
  key: string,
  name?: string,
  unit?: string,
  type: ChannelType,
  components?: string[],
  minimum?: number,
  maximum?: number,
}

export interface SensorData {
  id: string,
  meta?: Metadata,
  channelOrder?: string[],
  channelMap: Map<string, ChannelData>,
}

export interface ChannelData {
  meta?: MetadataChannel,
  timestamps: Date[],
  series: number[][],
}
