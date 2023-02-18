<script setup lang="ts">
import SensorView from './SensorView.vue';
import type { SensorData } from '@/protocol';
import { ref, watch } from 'vue';

const props = defineProps<{
  sensorOrder: string[],
  sensorMap: Map<string, SensorData>
}>()

let openSensors = ref(props.sensorOrder)

// When a new sensor is added, default it to open
watch(() => props.sensorOrder, (value, old) => {
  for(const id of value){
    if(!old.includes(id)){
      openSensors.value.push(id)
    }
  }
})
</script>

<template>
  <i-layout-content>
    <i-container>
      <h1 v-if="sensorOrder.length == 0">Waiting for data...</h1>
      <i-collapsible v-else v-model="openSensors">
        <SensorView v-for="sensorId in sensorOrder" :key="sensorId" :data="sensorMap.get(sensorId)!"></SensorView>
      </i-collapsible>
    </i-container>
  </i-layout-content>
</template>
