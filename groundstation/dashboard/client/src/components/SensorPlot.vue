<script setup lang="ts">
import { onMounted, ref, watch, type Ref } from 'vue';
import Plotly from 'plotly.js-dist-min'
import type { ChannelData } from '@/protocol';

const plotEl = ref<HTMLElement>()
const UPDATE_DELAY_MS = 100

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

let datarevision = 0

function getLayout(): Partial<Plotly.Layout> {
  const layout: Partial<Plotly.Layout> = {
    title: props.channel.meta?.name ?? props.channelKey,
    // margin: {
    //   l: 80,
    //   r: 40,
    //   t: 50,
    //   b: 40
    // },
    xaxis: {
      tickangle: 0
    },
    yaxis: {
      ticksuffix: props.channel.meta?.unit,
      range: props.channel.meta?.minimum != undefined && props.channel.meta?.maximum != undefined
        ? [props.channel.meta.minimum, props.channel.meta.maximum]
        : undefined,
    },
    uirevision: 'true', // Keep user zoom levels when updating data,
    datarevision: datarevision++
  }

  if(layout.yaxis?.ticksuffix == undefined && layout.yaxis?.range == undefined){
    delete layout.yaxis;
  }

  return layout
}

onMounted(() => {
  Plotly.newPlot(plotEl.value!, getTraces(), getLayout(), { displayModeBar: false, responsive: true })
})

let updateIsScheduled = false

watch(props.channel, () => {
  if (!updateIsScheduled) {
    setTimeout(doUpdate, UPDATE_DELAY_MS)
    updateIsScheduled = true
  }
})

function doUpdate() {
  Plotly.react(plotEl.value!, getTraces(), getLayout())
  updateIsScheduled = false
}
</script>

<template>
  <div class="plot" ref="plotEl"></div>
</template>

<style scoped>
.plot {
  height: 400px;
}
</style>
