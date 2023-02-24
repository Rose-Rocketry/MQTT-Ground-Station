<script setup lang="ts">
import SensorPlot from './SensorPlot.vue';
import type { SensorData } from '@/protocol';
import { computed } from 'vue';
import SensorLog from './SensorLog.vue';

const props = defineProps<{
  data: SensorData
}>()

const tableChannels = computed(() => {
  const keys = props.data.channelOrder ?? props.data.channelMap.keys()
  return [...keys].map(key => props.data.channelMap.get(key)!)
    .filter(channel => {
      const type = channel?.meta?.type
      return type == "string" || type == "bool" || type == undefined
    })
})

const plotChannelKeys = computed(() => {
  const keys = props.data.channelOrder ?? props.data.channelMap.keys()
  return [...keys].filter(key => {
    const type = props.data.channelMap.get(key)?.meta?.type
    return type == "number" || type == "vector"
  })
})
</script>

<template>
  <i-collapsible-item :name="data.id" :title="data.meta?.name ?? data.id">
    <i-container>
      <i-row v-if="plotChannelKeys.length > 0">
        <i-column xxl="4" lg="6" md="12" v-for="key in plotChannelKeys">
          <SensorPlot :key="key" :channel-key="key" :channel="props.data.channelMap.get(key)!"></SensorPlot>
        </i-column>
      </i-row>
      <i-row v-if="tableChannels.length > 0">
        <SensorLog :channels="tableChannels"></SensorLog>
      </i-row>
    </i-container>
  </i-collapsible-item>
</template>
