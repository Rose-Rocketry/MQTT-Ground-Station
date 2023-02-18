<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue';
import Plotly from 'plotly.js-dist-min'
import type { ChannelData } from '@/protocol';

const plotEl = ref<HTMLElement>()

const props = defineProps<{
  channelKey: string,
  channel: ChannelData,
}>()

function getTraces(): Plotly.Data[] {
  return props.channel.series.map((series, i) => {
    const data = {
      x: props.channel.timestamps,
      y: series,
      mode: 'lines',
      name: props.channel.meta?.components?.[i],
    };

    return data
  })
}

function getLayout(): Partial<Plotly.Layout> {
  return {
    title: props.channel.meta?.name ?? props.channelKey,
    margin: {
      l: 40,
      r: 40,
      t: 50,
      b: 40
    },
    xaxis: {
      tickangle: 0
    },
    yaxis: {
      ticksuffix: props.channel.meta?.unit,
      range: props.channel.meta?.minimum != undefined && props.channel.meta?.maximum != undefined
        ? [props.channel.meta.minimum, props.channel.meta.maximum]
        : undefined,
    },
    uirevision: 'true' // Keep user zoom levels when updating data
  }
}

onMounted(() => {
  Plotly.newPlot(plotEl.value!, getTraces(), getLayout(), { displayModeBar: false, responsive: true })
})

watch(props.channel, () => {
  Plotly.react(plotEl.value!, getTraces(), getLayout())
})
</script>

<template>
  <div class="plot" ref="plotEl"></div>
</template>

<style scoped>
.plot {
  height: 400px;
}
</style>
