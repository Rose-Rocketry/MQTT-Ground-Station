<script setup lang="ts">
import SensorPlot from './SensorPlot.vue';
import type { SensorData } from '@/protocol';
import { watch } from 'vue';

const props = defineProps<{
  data: SensorData
}>()
</script>

<template>
  <i-collapsible-item :name="data.id" :title="data.meta?.name ?? data.id">
    <i-container>
      <i-row>
        <i-column xxl="4" lg="6" md="12" v-for="key in (props.data.channelOrder ?? props.data.channelMap.keys())">
          <SensorPlot :key="key" :channel-key="key" :channel="props.data.channelMap.get(key)!"></SensorPlot>
        </i-column>
      </i-row>
    </i-container>
  </i-collapsible-item>
</template>
