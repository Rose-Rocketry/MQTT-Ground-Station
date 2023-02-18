<script setup lang="ts">
import SensorPlot from './SensorPlot.vue';
import { onUpdated } from 'vue';
import type { SensorData } from '@/protocol';

const { data } = defineProps<{
  data: SensorData
}>()
</script>

<template>
  <i-collapsible-item :name="data.id" :title="data.meta?.name ?? data.id">
    <i-container>
      <i-row>
        <i-column xxl="4" lg="6" md="12" v-for="key in data.channelOrder ?? data.channelMap.keys()" :key="key">
          <SensorPlot :channel-key="key" :channel="data.channelMap.get(key)!"></SensorPlot>
        </i-column>
      </i-row>
    </i-container>
  </i-collapsible-item>
</template>
